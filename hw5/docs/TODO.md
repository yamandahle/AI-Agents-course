# TODO — AirLLM Homework (HW5)

## Setup
- [x] Create virtual environment (uv or venv), Python 3.10/3.11
- [x] Install base dependencies: transformers, torch, airllm, psutil
- [x] Create Hugging Face account and get access token
- [x] Store HF token safely (env variable or .env file, never commit it)

## Step 1 — Model Selection
- [x] Choose text generation task
- [x] Select small model (fits in RAM, for Ollama baseline)
- [x] Select large model (too big for GPU/RAM, for AirLLM demo)
- [x] Verify licenses allow local use
- [x] Check VRAM requirements for both models

## Step 2 — Ollama Basic Inference
- [x] Install Ollama
- [x] Pull small model with `ollama pull`
- [x] Run test prompt and capture output
- [x] Confirm response is valid
- [x] Run via Ollama Python API with response time and token count
- [x] Save results to results/step2_results.json

## Step 3 — Baseline Failure
- [x] Load large model with standard transformers
- [x] Capture OOM error or slowness evidence
- [x] Save error log / screenshot as proof

## Step 4 — AirLLM Inference
- [x] Install airllm library
- [x] Load large model with AirLLM (layer-by-layer)
- [x] Run same test prompt
- [x] Confirm valid response is returned
- [x] Monitor and log RAM usage during inference

## Step 5 — Measurement and Comparison
- [x] Measure peak RAM for each method
- [x] Measure peak VRAM for each method
- [x] Measure time to first token
- [x] Measure total response time and tokens/sec
- [x] Build comparison table
- [x] Write latency vs memory tradeoff discussion

## Step 6 — Economic Analysis
- [x] Model cost per request for CPU on-prem, GPU on-prem, and cloud API (GPT-4o)
- [x] Calculate break-even point for GPU setup (~8,091 req/month)
- [x] Show CPU never breaks even (electricity > API cost per request)
- [x] Generate break-even graph (figures/break_even.png)
- [x] Save results to results/step6_economic_analysis.json

## Step 7 — TTFT & TPOT
- [x] Derive TTFT (Time To First Token) and TPOT (Time Per Output Token) from 3-token and 20-token runs
- [x] Explain prefill vs decode stages and why TPOT >> TTFT in AirLLM
- [x] TTFT = 15.5 s, TPOT = 57.6 s/token
- [x] Generate TTFT/TPOT bar chart (figures/ttft_tpot.png)
- [x] Save results to results/step7_ttft_tpot.json

## Step 8 — Quantization Levels Comparison
- [x] Benchmark FP32 vs INT8 vs INT4 on 3 real llama-13b layers
- [x] Implement custom INT4 quantization (2 nibbles per byte)
- [x] FP32=1210MB, INT8=302.5MB (4x), INT4=151.3MB (8x) per layer
- [x] Measure reconstruction error (MSE) for INT8 and INT4
- [x] Generate comparison chart (figures/quant_levels.png)
- [x] Save results to results/step8_quant_levels.json

## Step 9 — Dashboard
- [x] Unified 4-panel matplotlib chart combining all key results
- [x] Panels: RAM usage, tokens/sec, quantization memory, TTFT/TPOT
- [x] Save to figures/dashboard.png

## Step 10 — Original Extension: Scaling Projection
- [x] Project AirLLM memory advantage across 7B / 13B / 30B / 70B / 405B models
- [x] Show memory saving ratio grows from 7.8x (7B) to 48.2x (405B)
- [x] Generate scaling chart (figures/scaling.png)
- [x] Save results to results/step10_scaling.json

## Final
- [x] Clean up all scripts, keep every .py file under 150 lines
- [x] Make sure no HF token or secret is exposed or committed
- [x] Fix all git path case issues (HW5/ -> hw5/)
- [x] Review against PRD success criteria
- [x] Submit
