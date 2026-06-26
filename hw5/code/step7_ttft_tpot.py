"""
Step 7 — TTFT & TPOT Analysis
Time To First Token (TTFT) vs Time Per Output Token (TPOT) for AirLLM.

AirLLM loads every layer from disk for BOTH prefill and decode,
so TTFT ≠ TPOT: prefill processes all input tokens in one pass,
decode processes one output token per pass.

Method: solve a 2-equation system using the 3-token and 20-token runs.
  TTFT + 2·TPOT  = t3   (3 output tokens → 1 TTFT + 2 decode steps)
  TTFT + 19·TPOT = t20  (20 output tokens → 1 TTFT + 19 decode steps)
"""
import json, math, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR  = Path(__file__).parent.parent / "figures"

def load_json(name):
    return json.loads((RESULTS_DIR / name).read_text())

def solve_ttft_tpot(t_n1, n1, t_n2, n2):
    """Solve: TTFT + (n-1)*TPOT = t for two (n, t) pairs."""
    d_tpot = (t_n2 - t_n1) / ((n2 - 1) - (n1 - 1))
    ttft   = t_n1 - (n1 - 1) * d_tpot
    return ttft, d_tpot

def make_chart(ttft, tpot, tok3, tok20, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: TTFT vs TPOT bar
    ax = axes[0]
    bars = ax.bar(["TTFT\n(prefill+1st token)", "TPOT\n(each decode token)"],
                  [ttft, tpot], color=["steelblue", "darkorange"], width=0.5)
    for bar, val in zip(bars, [ttft, tpot]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.1f}s", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylabel("Seconds", fontsize=12)
    ax.set_title("AirLLM: TTFT vs TPOT\nhuggyllama/llama-13b on CPU", fontsize=12)
    ax.set_ylim(0, max(ttft, tpot) * 1.25)
    ax.grid(axis="y", alpha=0.3)

    # Right: predicted vs actual total inference time
    ax2 = axes[1]
    ns  = [3, 20]
    pred = [ttft + (n - 1) * tpot for n in ns]
    actual = [tok3, tok20]
    x = range(len(ns))
    w = 0.3
    b1 = ax2.bar([i - w/2 for i in x], actual, w, label="Measured", color="steelblue")
    b2 = ax2.bar([i + w/2 for i in x], pred,   w, label="Predicted (TTFT+TPOT model)",
                 color="darkorange", alpha=0.8)
    ax2.set_xticks(list(x)); ax2.set_xticklabels([f"{n} tokens" for n in ns])
    ax2.set_ylabel("Total inference time (s)", fontsize=12)
    ax2.set_title("Model fit: predicted vs measured\ntotal inference time", fontsize=12)
    ax2.legend(); ax2.grid(axis="y", alpha=0.3)
    for bar in list(b1) + list(b2):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f"{bar.get_height():.0f}s", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(str(out_path), dpi=150, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    r3  = load_json("step4a_results.json")
    r20 = load_json("step4a_20tokens_results.json")

    t3, n3   = r3["inference_time_sec"],  r3["new_tokens"]   # 130.56 s, 3 tok
    t20, n20 = r20["inference_time_sec"], r20["new_tokens"]  # 1108.91 s, 20 tok

    ttft, tpot = solve_ttft_tpot(t3, n3, t20, n20)

    total_output_tokens = 20
    predicted_latency   = ttft + (total_output_tokens - 1) * tpot
    avg_tok_per_sec     = total_output_tokens / (ttft + (total_output_tokens - 1) * tpot)

    print("\n" + "="*56)
    print("  TTFT & TPOT — AirLLM CPU (huggyllama/llama-13b)")
    print("="*56)
    print(f"  Measured 3-token  run  : {t3:.2f} s")
    print(f"  Measured 20-token run  : {t20:.2f} s")
    print(f"  -> TTFT (prefill stage) : {ttft:.1f} s")
    print(f"  -> TPOT (per decode tok): {tpot:.1f} s/token")
    print(f"  Predicted 20-tok total : {predicted_latency:.1f} s  (actual: {t20:.1f} s)")
    print(f"  Decode throughput      : {1/tpot:.4f} tok/s")
    print()
    print("  Why TTFT < TPOT?")
    print("  AirLLM prefill processes ALL input tokens in one fwd pass.")
    print("  Decode runs a separate fwd pass PER output token, each time")
    print("  reloading all 40 layers from disk via mmap.")
    print("="*56)

    fig_path = FIGURES_DIR / "ttft_tpot.png"
    make_chart(ttft, tpot, t3, t20, fig_path)
    print(f"\nChart saved -> {fig_path}")

    result = {
        "timestamp": datetime.now().isoformat(),
        "model": r3["model"],
        "hardware": r3["hardware"],
        "method": "linear system from 3-token and 20-token measured runs",
        "input_data": {
            "run_3_tokens_sec":  t3,
            "run_20_tokens_sec": t20,
        },
        "ttft_sec": round(ttft, 2),
        "tpot_sec": round(tpot, 2),
        "decode_tok_per_sec": round(1 / tpot, 5),
        "note": (
            "TTFT covers tokenization + prefill (one fwd pass over all 40 layers "
            "for the input tokens). TPOT is one fwd pass per output token — "
            "AirLLM reloads all layers from disk for every decode step because "
            "KV cache is not kept in RAM between tokens."
        ),
    }
    out_json = RESULTS_DIR / "step7_ttft_tpot.json"
    out_json.write_text(json.dumps(result, indent=2))
    print(f"JSON  saved -> {out_json}")
