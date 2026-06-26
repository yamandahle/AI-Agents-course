import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR  = Path(__file__).parent.parent / "figures"

def load(name):
    return json.loads((RESULTS_DIR / name).read_text())

if __name__ == "__main__":
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    r2   = load("step2_results.json")[0]
    r4a  = load("step4a_20tokens_results.json")
    r4b  = load("step4b_results.json")
    r7   = load("step7_ttft_tpot.json")
    r8   = load("step8_quant_levels.json")
    r6   = load("step6_economic_analysis.json")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "HW5 — AirLLM Complete Results Dashboard\n"
        "Model: huggyllama/llama-13b (26 GB) on CPU",
        fontsize=14, fontweight="bold"
    )

    # ── Panel 1: RAM usage ───────────────────────────────────────────
    ax = axes[0, 0]
    labels = ["Phi3-mini\n(Ollama)", "AirLLM\nFP32", "AirLLM\nINT8 bench"]
    ram    = [0.5, r4a["peak_ram_gb"], r4b["peak_ram_gb"]]
    colors = ["steelblue", "darkorange", "firebrick"]
    bars = ax.bar(labels, ram, color=colors)
    ax.axhline(y=14.56, color="red", ls="--", lw=1.5, label="T4 VRAM limit (14.56 GB)")
    ax.axhline(y=16.8,  color="gray", ls=":",  lw=1.5, label="System RAM (16.8 GB)")
    for bar, v in zip(bars, ram):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.1,
                f"{v:.2f} GB", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Peak RAM (GB)"); ax.set_ylim(0, 18)
    ax.set_title("Peak RAM Usage per Method")
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)

    # ── Panel 2: Tokens/sec comparison ──────────────────────────────
    ax = axes[0, 1]
    spd_labels = ["Phi3-mini\n(Ollama)", "AirLLM FP32\n(20 tokens)", "AirLLM INT8\n(3 tokens)"]
    speeds     = [r2["tokens_per_sec"], r4a["tokens_per_sec"], r4b["tokens_per_sec"]]
    bars2 = ax.bar(spd_labels, speeds, color=["steelblue", "darkorange", "firebrick"])
    for bar, v in zip(bars2, speeds):
        ax.text(bar.get_x() + bar.get_width()/2, v + v * 0.03,
                f"{v:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Tokens / second"); ax.set_yscale("log")
    ax.set_title("Inference Speed (log scale)")
    ax.grid(axis="y", alpha=0.3)

    # ── Panel 3: Quantization memory per layer ───────────────────────
    ax = axes[1, 0]
    avg = r8["averages"]
    q_levels = ["FP32", "INT8\n(4x)", "INT4\n(8x)"]
    q_mb     = [avg["fp32_mb"], avg["int8_mb"], avg["int4_mb"]]
    q_colors = ["steelblue", "darkorange", "firebrick"]
    bars3 = ax.bar(q_levels, q_mb, color=q_colors)
    for bar, v in zip(bars3, q_mb):
        ax.text(bar.get_x() + bar.get_width()/2, v + 10,
                f"{v:.0f} MB", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Size per Layer (MB)")
    ax.set_title("Memory per Layer by Quantization Level")
    # annotate MSEs
    ax.text(1, avg["int8_mb"] / 2, f"MSE\n{avg['int8_mse']:.1e}", ha="center",
            va="center", fontsize=9, color="white", fontweight="bold")
    ax.text(2, avg["int4_mb"] / 2, f"MSE\n{avg['int4_mse']:.1e}", ha="center",
            va="center", fontsize=9, color="white", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    # ── Panel 4: TTFT vs TPOT ───────────────────────────────────────
    ax = axes[1, 1]
    ttft = r7["ttft_sec"]; tpot = r7["tpot_sec"]
    bars4 = ax.bar(["TTFT\n(prefill)", "TPOT\n(per decode token)"],
                   [ttft, tpot], color=["steelblue", "firebrick"])
    for bar, v in zip(bars4, [ttft, tpot]):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.5,
                f"{v:.1f} s", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylabel("Seconds")
    ax.set_title(f"TTFT vs TPOT — AirLLM CPU\nTTFT={ttft}s | TPOT={tpot}s/token")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = FIGURES_DIR / "dashboard.png"
    plt.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Dashboard saved -> {out}")
