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

## Final
- [x] Clean up notebook / script, add clear output cells
- [x] Make sure no token or secret is exposed
- [x] Review against PRD success criteria
- [x] Submit
