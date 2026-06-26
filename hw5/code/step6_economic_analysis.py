"""
Step 6 - Economic Analysis: On-Premises vs Cloud API
Compares cost of running huggyllama/llama-13b three ways:
  1. CPU-only On-Prem (AirLLM on this laptop)
  2. GPU On-Prem (hypothetical RTX 3080)
  3. Cloud API (GPT-4o pricing)
Finds break-even point and saves graph + JSON.
"""
import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR = Path(__file__).parent.parent / "figures"

# ── Hardware assumptions ────────────────────────────────────────────
CPU_COST_USD        = 900       # laptop purchase price
CPU_WATTS           = 30        # avg power during inference
CPU_TOK_PER_SEC     = 0.018     # measured in Step 4a

GPU_COST_USD        = 500       # RTX 3080 used market price
GPU_WATTS           = 320       # TDP
GPU_TOK_PER_SEC     = 5.0       # realistic for llama-13b on RTX 3080

HW_LIFE_YEARS       = 3
ELEC_USD_PER_KWH    = 0.15

# ── Request profile ─────────────────────────────────────────────────
INPUT_TOKENS        = 100
OUTPUT_TOKENS       = 200

# ── API pricing: GPT-4o ─────────────────────────────────────────────
API_IN_PER_1M       = 2.50
API_OUT_PER_1M      = 10.00
API_COST_PER_REQ    = (INPUT_TOKENS * API_IN_PER_1M +
                       OUTPUT_TOKENS * API_OUT_PER_1M) / 1_000_000

N = np.arange(0, 200_001, 500)

def monthly_cost(hw_cost, watts, tok_s, n_reqs):
    fixed   = hw_cost / (HW_LIFE_YEARS * 12)
    t_hrs   = OUTPUT_TOKENS / tok_s / 3600
    kwh_req = watts * t_hrs / 1000
    elec    = kwh_req * ELEC_USD_PER_KWH
    return fixed + elec * n_reqs, fixed, elec

def breakeven(fixed, elec_per_req):
    diff = API_COST_PER_REQ - elec_per_req
    return fixed / diff if diff > 0 else None

if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    cpu_total, cpu_fixed, cpu_elec = monthly_cost(CPU_COST_USD, CPU_WATTS, CPU_TOK_PER_SEC, N)
    gpu_total, gpu_fixed, gpu_elec = monthly_cost(GPU_COST_USD, GPU_WATTS, GPU_TOK_PER_SEC, N)
    api_total = API_COST_PER_REQ * N

    cpu_be = breakeven(cpu_fixed, cpu_elec)
    gpu_be = breakeven(gpu_fixed, gpu_elec)

    print("\n" + "="*54)
    print("  Economic Analysis: On-Prem vs API (GPT-4o)")
    print("="*54)
    print(f"  Request: {INPUT_TOKENS} input + {OUTPUT_TOKENS} output tokens")
    print(f"  API cost/request:        ${API_COST_PER_REQ:.5f}")
    print(f"  CPU elec/request:        ${cpu_elec:.5f}  ({OUTPUT_TOKENS/CPU_TOK_PER_SEC:.0f}s/req)")
    print(f"  GPU elec/request:        ${gpu_elec:.5f}  ({OUTPUT_TOKENS/GPU_TOK_PER_SEC:.0f}s/req)")
    print(f"  CPU fixed/month:         ${cpu_fixed:.2f}")
    print(f"  GPU fixed/month:         ${gpu_fixed:.2f}")
    if cpu_be:
        print(f"  CPU break-even:          {cpu_be:,.0f} req/month")
    else:
        print(f"  CPU break-even:          NEVER (elec > API cost per request)")
    if gpu_be:
        print(f"  GPU break-even:          {gpu_be:,.0f} req/month ({gpu_be/30:.0f}/day)")
    print("="*54)

    # Graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(N/1000, api_total, 'b-',  lw=2.5, label=f'API GPT-4o (${API_COST_PER_REQ:.4f}/req)')
    ax.plot(N/1000, gpu_total, 'g-',  lw=2.5, label=f'GPU On-Prem RTX 3080 (${gpu_fixed:.0f}/mo fixed)')
    ax.plot(N/1000, cpu_total, 'r--', lw=2,   label=f'CPU On-Prem AirLLM (${cpu_fixed:.0f}/mo fixed)')

    if gpu_be and gpu_be <= N[-1]:
        be_cost = API_COST_PER_REQ * gpu_be
        ax.axvline(x=gpu_be/1000, color='green', ls=':', alpha=0.6)
        ax.plot(gpu_be/1000, be_cost, 'g^', ms=12, zorder=5,
                label=f'Break-even: {gpu_be:,.0f} req/mo ({gpu_be/30:.0f}/day)')
        ax.annotate(f'  {int(gpu_be):,} req/mo', xy=(gpu_be/1000, be_cost),
                    fontsize=9, color='green', va='bottom')

    ax.set_xlabel('Requests per Month (thousands)', fontsize=12)
    ax.set_ylabel('Monthly Cost (USD)', fontsize=12)
    ax.set_title(
        'On-Premises vs API — Monthly Cost Comparison\n'
        'Model: huggyllama/llama-13b | 100 input + 200 output tokens/request',
        fontsize=12)
    ax.legend(fontsize=10); ax.grid(True, alpha=0.3)
    ax.set_xlim(0); ax.set_ylim(0)
    plt.tight_layout()
    out_fig = FIGURES_DIR / "break_even.png"
    plt.savefig(str(out_fig), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nGraph saved -> {out_fig}")

    result = {
        "timestamp": datetime.now().isoformat(),
        "assumptions": {
            "input_tokens_per_request": INPUT_TOKENS,
            "output_tokens_per_request": OUTPUT_TOKENS,
            "electricity_usd_per_kwh": ELEC_USD_PER_KWH,
            "hardware_lifetime_years": HW_LIFE_YEARS,
            "api": "GPT-4o ($2.50 input / $10.00 output per 1M tokens)",
        },
        "cpu_on_prem": {
            "hardware_cost_usd": CPU_COST_USD,
            "fixed_monthly_usd": round(cpu_fixed, 2),
            "electricity_per_request_usd": round(cpu_elec, 5),
            "tokens_per_sec": CPU_TOK_PER_SEC,
            "inference_time_sec": round(OUTPUT_TOKENS / CPU_TOK_PER_SEC),
            "break_even": "NEVER - electricity cost per request exceeds API price",
        },
        "gpu_on_prem": {
            "hardware_cost_usd": GPU_COST_USD,
            "fixed_monthly_usd": round(gpu_fixed, 2),
            "electricity_per_request_usd": round(gpu_elec, 5),
            "tokens_per_sec": GPU_TOK_PER_SEC,
            "inference_time_sec": round(OUTPUT_TOKENS / GPU_TOK_PER_SEC),
            "break_even_requests_per_month": int(gpu_be) if gpu_be else "NEVER",
            "break_even_requests_per_day": int(gpu_be / 30) if gpu_be else "NEVER",
        },
        "api_gpt4o": {
            "cost_per_request_usd": round(API_COST_PER_REQ, 5),
        },
        "recommendation": (
            "CPU-only AirLLM is NOT economically competitive with cloud API: "
            f"electricity alone costs ${cpu_elec:.4f}/request vs API ${API_COST_PER_REQ:.4f}/request. "
            f"A GPU setup (RTX 3080) breaks even at ~{int(gpu_be):,} requests/month. "
            "AirLLM's real value is CAPABILITY (running models APIs don't expose) and PRIVACY (data never leaves your machine)."
        ),
    }
    (RESULTS_DIR / "step6_economic_analysis.json").write_text(json.dumps(result, indent=2))
    print(f"JSON  saved -> {RESULTS_DIR / 'step6_economic_analysis.json'}")
