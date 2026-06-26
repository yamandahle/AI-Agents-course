"""
Step 5 — Final Comparison Table
Reads all result JSON files and prints the full 3-way comparison:
  Step 3: T4 GPU → OOM
  Step 4a: AirLLM CPU FP32 → success
  Step 4b: AirLLM CPU + INT8 benchmark → 4x compression
"""
import json
from pathlib import Path

RESULTS = Path(__file__).parent.parent / "results"

STEP3 = {
    "hardware":       "T4 GPU (Google Colab)",
    "model":          "huggyllama/llama-13b",
    "vram_gb":        14.56,
    "model_size_gb":  26.0,
    "compression":    "none (FP16)",
    "peak_mem":       "14.56GB VRAM",
    "status":         "OOM at 58% loading",
    "response":       "N/A",
    "tokens":         "N/A",
    "tokens_per_sec": "N/A",
    "infer_time":     "N/A",
}

def load(name):
    p = RESULTS / name
    if p.exists():
        return json.loads(p.read_text())
    return None

if __name__ == "__main__":
    a = load("step4a_20tokens_results.json")
    b = load("step4b_results.json")

    if not a:
        print("Missing step4a_20tokens_results.json — run step4_airllm_cpu.py first")
        raise SystemExit(1)
    if not b:
        print("Missing step4b_results.json — run step4b_cpu_quant.py first")
        raise SystemExit(1)

    W = 18
    rows = [
        ("Model",          "huggyllama/llama-13b",  "huggyllama/llama-13b",   "huggyllama/llama-13b"),
        ("Model size",     "26GB (FP16)",            "26GB (FP16 on disk)",    "26GB (FP16 on disk)"),
        ("Hardware",       "T4 GPU",                 "CPU (Intel Iris Xe)",    "CPU (Intel Iris Xe)"),
        ("Memory avail",   "14.56GB VRAM",           "16.8GB RAM",             "16.8GB RAM"),
        ("Method",         "Standard load",          "AirLLM mmap layers",     "AirLLM + INT8 bench"),
        ("Compression",    "none",                   "none (FP32)",            "INT8 (4x ratio)"),
        ("Peak mem used",  "14.56GB->OOM",          f"{a['peak_ram_gb']}GB RAM", f"{b['peak_ram_gb']}GB RAM"),
        ("Status",         "FAILED (OOM)",           "SUCCESS",                "SUCCESS"),
        ("Prompt",         "N/A",                    a.get("prompt",""),       b.get("prompt","")),
        ("Response",       "N/A",                    a.get("response","")[:22], b.get("response","")[:22]),
        ("New tokens",     "N/A",                    str(a.get("new_tokens")), str(b.get("new_tokens"))),
        ("Infer time",     "N/A",                   f"{a['inference_time_sec']}s", f"{b['inference_time_sec']}s"),
        ("Tokens/sec",     "N/A",                    str(a.get("tokens_per_sec")), str(b.get("tokens_per_sec"))),
        ("INT8 layer size","N/A",                    "N/A",                   f"317.2MB (vs 1268.8MB)"),
        ("INT8 est. model","N/A",                    "N/A",                   f"{b['full_model_int8_gb']}GB (vs ~50.8GB FP32)"),
    ]

    sep = "=" * (24 + W*3 + 6)
    print(f"\n{sep}")
    print(f"  FINAL COMPARISON - HW5 AirLLM Proof")
    print(f"{sep}")
    print(f"  {'Metric':<22}  {'Step 3':>{W}}  {'Step 4a':>{W}}  {'Step 4b':>{W}}")
    print(f"  {'-'*(22 + W*3 + 6)}")
    for r in rows:
        print(f"  {r[0]:<22}  {str(r[1]):>{W}}  {str(r[2]):>{W}}  {str(r[3]):>{W}}")
    print(f"{sep}")
    print(f"  Key insight: AirLLM loads 1 layer (~0.65GB) at a time via mmap.")
    print(f"  A 26GB model that OOM'd on a 14.56GB GPU runs in ~2-3GB RAM on CPU.")
    print(f"  INT8 quantization reduces each layer from 1268.8MB to 317.2MB (4x).")
    print(f"{sep}\n")

    summary = {
        "step3_gpu_oom": STEP3,
        "step4a_airllm_cpu_fp32": {k: a.get(k) for k in
            ["model","hardware","peak_ram_gb","response","new_tokens","inference_time_sec","tokens_per_sec","status"]},
        "step4b_airllm_cpu_int8bench": {k: b.get(k) for k in
            ["model","hardware","peak_ram_gb","response","new_tokens","inference_time_sec","tokens_per_sec",
             "compression_ratio","full_model_int8_gb","status"]},
    }
    out = RESULTS / "step5_comparison.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"Saved -> {out}")
