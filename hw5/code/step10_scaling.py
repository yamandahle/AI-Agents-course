"""
Step 10 — Original Extension: AirLLM Scaling Projection
Shows how AirLLM's memory advantage grows with model size.
For standard loading: VRAM needed = model_size_fp16.
For AirLLM: peak RAM stays ~1 layer regardless of total size.
Projects across 7B, 13B, 30B, 70B, 405B parameter models.
"""
import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR  = Path(__file__).parent.parent / "figures"

# Known model architectures: (params_B, n_layers, hidden_dim)
MODELS = [
    ("LLaMA-7B",   7,   32, 4096),
    ("LLaMA-13B",  13,  40, 5120),
    ("LLaMA-30B",  30,  60, 6656),
    ("LLaMA-70B",  70,  80, 8192),
    ("LLaMA-405B", 405, 126, 16384),
]

MEASURED_LAYER_GB = 1.21    # step8: actual layer size for 13B (avg 1210 MB)
MEASURED_N_LAYERS = 40      # 13B has 40 layers
AIRLLM_OVERHEAD_GB = 0.8    # tokenizer, embeddings, fixed overhead

def layer_size_gb(hidden, n_layers):
    """Estimate one transformer layer size in FP32 (bytes = params * 4)."""
    # MHA: 4 weight matrices of (hidden x hidden) + MLP: 3 matrices (hidden x 4*hidden)
    attn   = 4 * hidden * hidden
    mlp    = 3 * hidden * 4 * hidden
    return (attn + mlp) * 4 / 1024**3

def model_fp16_gb(params_b):
    return params_b * 2  # 2 bytes per param in FP16

def airllm_ram_gb(hidden, n_layers):
    return layer_size_gb(hidden, n_layers) + AIRLLM_OVERHEAD_GB

if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, params, n_layers, hidden in MODELS:
        fp16_gb   = model_fp16_gb(params)
        airllm_gb = airllm_ram_gb(hidden, n_layers)
        layer_gb  = layer_size_gb(hidden, n_layers)
        saving    = fp16_gb / airllm_gb
        rows.append({
            "model":        name,
            "params_b":     params,
            "fp16_gb":      round(fp16_gb, 1),
            "airllm_gb":    round(airllm_gb, 2),
            "layer_gb":     round(layer_gb, 2),
            "memory_saving": round(saving, 1),
        })

    print("\n" + "="*66)
    print("  AirLLM Scaling Projection")
    print("="*66)
    print(f"  {'Model':<14} {'FP16 size':>10} {'AirLLM RAM':>11} {'Saving':>8}")
    print(f"  {'-'*14} {'-'*10} {'-'*11} {'-'*8}")
    for r in rows:
        fits = "YES" if r["fp16_gb"] <= 14.56 else "OOM on T4"
        print(f"  {r['model']:<14} {r['fp16_gb']:>8.1f}GB "
              f"{r['airllm_gb']:>9.2f}GB  {r['memory_saving']:>6.1f}x  ({fits})")
    print("="*66)

    names  = [r["model"] for r in rows]
    fp16   = [r["fp16_gb"]   for r in rows]
    air    = [r["airllm_gb"] for r in rows]
    x = range(len(names))
    w = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    bars_fp = ax1.bar([i - w/2 for i in x], fp16, w, label="FP16 Standard Load", color="firebrick", alpha=0.85)
    bars_air= ax1.bar([i + w/2 for i in x], air,  w, label="AirLLM Peak RAM",    color="steelblue")
    ax1.axhline(y=14.56, color="red",  ls="--", lw=1.5, label="T4 VRAM (14.56 GB)")
    ax1.axhline(y=16.8,  color="gray", ls=":",  lw=1.5, label="Laptop RAM (16.8 GB)")
    ax1.axhline(y=24,    color="purple", ls="-.", lw=1.5, label="RTX 3090 VRAM (24 GB)")
    ax1.set_yscale("log")
    ax1.set_xticks(list(x)); ax1.set_xticklabels(names, rotation=15, ha="right")
    ax1.set_ylabel("Memory (GB, log scale)"); ax1.legend(fontsize=8)
    ax1.set_title("Standard Load vs AirLLM Peak RAM\nacross model sizes")
    ax1.grid(axis="y", alpha=0.3)

    savings = [r["memory_saving"] for r in rows]
    bars_s = ax2.bar(names, savings, color="steelblue")
    for bar, v in zip(bars_s, savings):
        ax2.text(bar.get_x() + bar.get_width()/2, v + 1,
                 f"{v:.0f}x", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Memory Saved (FP16 load / AirLLM RAM)")
    ax2.set_title("AirLLM Memory Saving Ratio vs Model Size\nlarger models = bigger advantage")
    ax2.set_xticks(range(len(names))); ax2.set_xticklabels(names, rotation=15, ha="right")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = FIGURES_DIR / "scaling.png"
    plt.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nChart saved -> {out}")

    result = {
        "timestamp": datetime.now().isoformat(),
        "description": "AirLLM scaling projection across model sizes",
        "note": "Layer sizes estimated from known LLaMA architecture (MHA + MLP weights in FP32)",
        "models": rows,
    }
    json_path = RESULTS_DIR / "step10_scaling.json"
    json_path.write_text(json.dumps(result, indent=2))
    print(f"JSON  saved -> {json_path}")
