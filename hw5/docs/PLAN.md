# PLAN — AirLLM Homework (HW5)

## Step 1 — Choose Task and Model
- Task: simple text generation (question answering)
- Small model: `microsoft/Phi-3-mini-4k-instruct` via Ollama as `phi3:mini` (~2 GB)
- Large model: `huggyllama/llama-13b` (~26 GB FP16, no HF token required)
- Prompt used throughout: "What is the capital of Spain?"

## Step 2 — Install Ollama and Run Basic Inference
- Install Ollama, pull phi3:mini
- Run test prompt via Ollama REST API, measure tokens/sec
- Save results to results/step2_results.json

## Step 3 — Baseline: Attempt to Load a Too-Large Model Normally
- Load huggyllama/llama-13b on a T4 GPU (14.56 GB VRAM) via standard transformers
- Crash at 58% load — RuntimeError: CUDA out of memory
- Save error screenshot as proof

## Step 4 — AirLLM: Run the Same Large Model on CPU
- Environment: Python 3.11, uv venv, transformers==4.38.2 (required for AirLLM + LLaMA)
- Key settings: device="cpu", dtype=torch.float32
- Run 1: 3 tokens — 130.56 s, peak RAM 2.47 GB
- Run 2: 20 tokens — 1108.91 s, peak RAM 2.42 GB
- INT8 benchmark (step4b): torch.quantize_per_tensor on 3 real layers, then AirLLM inference

## Step 5 — Measure and Compare
- 3-way comparison: GPU OOM vs AirLLM FP32 vs AirLLM INT8
- Results saved to results/step5_comparison.json

## Step 6 — Economic Analysis
- Compare CPU on-prem, GPU on-prem (RTX 3080), and GPT-4o API
- CPU never breaks even (electricity $0.0139/req > API $0.00225/req)
- GPU breaks even at ~8,091 req/month

## Step 7 — TTFT & TPOT
- Derive from two existing runs using linear equation system
- TTFT = 15.5 s (prefill), TPOT = 57.6 s/token (decode)
- AirLLM has no KV cache in RAM — every decode step reloads all 40 layers

## Step 8 — Quantization Levels
- Benchmark FP32 / INT8 / INT4 on real llama-13b layers
- INT4: custom nibble packing (2 values per byte, range -8..7)
- FP32=1210MB, INT8=302.5MB, INT4=151.3MB per layer

## Step 9 — Dashboard
- Unified 4-panel chart: RAM, tokens/sec, quantization memory, TTFT/TPOT

## Step 10 — Scaling Projection (Original Extension)
- Project AirLLM memory advantage to 7B / 13B / 30B / 70B / 405B
- Memory saving grows from 7.8x to 48.2x — shows AirLLM is more valuable at larger scale

## Environment Setup
- Python version: 3.11 (via uv)
- Virtual environment: `uv venv .venv --python 3.11`
- Key dependencies: `transformers==4.38.2`, `torch` (CPU), `airllm`, `psutil`, `safetensors`, `matplotlib`
- Setup automated in `setup_hw5.bat`
