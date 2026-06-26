import json, time, gc
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from safetensors import safe_open

SHARD_DIR = (
    Path.home() / ".cache/huggingface/hub"
    / "models--huggyllama--llama-13b"
    / "snapshots/bf57045473f207bb1de1ed035ace226f4d9f9bba/splitted_model"
)
RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR  = Path(__file__).parent.parent / "figures"
N_LAYERS = 3

def quantize_int8(t):
    scale = t.abs().max() / 127.0
    return torch.quantize_per_tensor(t.float(), float(scale), 0, torch.qint8)

def quantize_int4(t):
    scale = t.abs().max() / 7.0
    q4 = (t.float() / scale).round().clamp(-8, 7).to(torch.int8)
    flat = q4.flatten()
    if flat.numel() % 2 != 0:
        flat = torch.cat([flat, torch.zeros(1, dtype=torch.int8)])
    packed = (flat[0::2] & 0x0F) | ((flat[1::2] << 4) & 0xF0)
    return packed, scale, q4.shape

def dequantize_int4(packed, scale, shape):
    lo = (packed & 0x0F).to(torch.int8)
    lo = torch.where(lo >= 8, lo - 16, lo)
    hi = ((packed >> 4) & 0x0F).to(torch.int8)
    hi = torch.where(hi >= 8, hi - 16, hi)
    flat = torch.empty(lo.numel() + hi.numel(), dtype=torch.int8)
    flat[0::2] = lo; flat[1::2] = hi
    return flat[:shape.numel()].float().reshape(shape) * scale

def mse(a, b):
    return float(((a.float() - b.float()) ** 2).mean())

def load_layer(idx):
    path = SHARD_DIR / f"model.layers.{idx}.safetensors"
    tensors = {}
    with safe_open(str(path), framework="pt", device="cpu") as f:
        for key in f.keys():
            tensors[key] = f.get_tensor(key)
    return tensors

def flat_weights(tensors):
    return torch.cat([t.flatten().float() for t in tensors.values()])

if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for i in range(N_LAYERS):
        print(f"\nLayer {i} ...", flush=True)
        orig = flat_weights(load_layer(i))
        fp32_mb = orig.numel() * 4 / 1024 / 1024

        t0 = time.perf_counter()
        q8 = quantize_int8(orig)
        t8 = time.perf_counter() - t0
        dq8 = q8.dequantize()

        t0 = time.perf_counter()
        packed, sc, sh = quantize_int4(orig)
        t4 = time.perf_counter() - t0
        dq4 = dequantize_int4(packed, sc, sh)

        rows.append({
            "layer":      i,
            "fp32_mb":    round(fp32_mb, 1),
            "int8_mb":    round(fp32_mb / 4, 1),
            "int4_mb":    round(fp32_mb / 8, 1),
            "int8_ratio": 4.0,
            "int4_ratio": 8.0,
            "int8_ms":    round(t8 * 1000, 1),
            "int4_ms":    round(t4 * 1000, 1),
            "int8_mse":   round(mse(orig, dq8), 8),
            "int4_mse":   round(mse(orig, dq4), 8),
        })
        del orig, q8, dq8, packed, dq4; gc.collect()

    avg = {k: sum(r[k] for r in rows) / N_LAYERS for k in rows[0] if k != "layer"}
    print("\n" + "="*56)
    print("  Quantization Levels: FP32 vs INT8 vs INT4")
    print("="*56)
    print(f"  FP32 per layer : {avg['fp32_mb']:.1f} MB  (baseline)")
    print(f"  INT8 per layer : {avg['int8_mb']:.1f} MB  (4x smaller, MSE {avg['int8_mse']:.2e})")
    print(f"  INT4 per layer : {avg['int4_mb']:.1f} MB  (8x smaller, MSE {avg['int4_mse']:.2e})")
    full = {
        "fp32": round(avg["fp32_mb"] * 40 / 1024, 1),
        "int8": round(avg["int8_mb"] * 40 / 1024, 1),
        "int4": round(avg["int4_mb"] * 40 / 1024, 1),
    }
    print(f"  Full model est.: FP32={full['fp32']}GB  INT8={full['int8']}GB  INT4={full['int4']}GB")
    print("="*56)

    levels = ["FP32", "INT8", "INT4"]
    mb_vals = [avg["fp32_mb"], avg["int8_mb"], avg["int4_mb"]]
    mse_vals = [0, avg["int8_mse"], avg["int4_mse"]]
    colors = ["steelblue", "darkorange", "firebrick"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    bars = ax1.bar(levels, mb_vals, color=colors)
    for bar, v in zip(bars, mb_vals):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f"{v:.0f} MB", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Size per Layer (MB)"); ax1.grid(axis="y", alpha=0.3)
    ax1.set_title("Memory per Layer by Quantization Level\nhuggyllama/llama-13b")

    ax2.bar(levels[1:], mse_vals[1:], color=colors[1:])
    for j, v in enumerate(mse_vals[1:]):
        ax2.text(j, v * 1.05, f"{v:.2e}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Reconstruction Error (MSE)"); ax2.grid(axis="y", alpha=0.3)
    ax2.set_title("Quantization Error vs FP32\nLower = more accurate")

    plt.tight_layout()
    fig_path = FIGURES_DIR / "quant_levels.png"
    plt.savefig(str(fig_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nChart  saved -> {fig_path}")

    out = {
        "timestamp": datetime.now().isoformat(),
        "model": "huggyllama/llama-13b",
        "layers_benchmarked": N_LAYERS,
        "per_layer": rows,
        "averages": {k: round(v, 4) for k, v in avg.items()},
        "full_model_estimate_gb": full,
    }
    json_path = RESULTS_DIR / "step8_quant_levels.json"
    json_path.write_text(json.dumps(out, indent=2))
    print(f"JSON   saved -> {json_path}")
