# TODO — AirLLM Homework (HW5)

## Setup
- [ ] Create virtual environment (uv or venv), Python 3.10/3.11
- [ ] Install base dependencies: transformers, torch, airllm, psutil
- [ ] Create Hugging Face account and get access token
- [ ] Store HF token safely (env variable or .env file, never commit it)

## Step 1 — Model Selection
- [ ] Choose text generation task
- [ ] Select small model (fits in RAM, for Ollama baseline)
- [ ] Select large model (too big for GPU/RAM, for AirLLM demo)
- [ ] Verify licenses allow local use
- [ ] Check VRAM requirements for both models

## Step 2 — Ollama Basic Inference
- [ ] Install Ollama
- [ ] Pull small model with `ollama pull`
- [ ] Run test prompt and capture output
- [ ] Confirm response is valid

## Step 3 — Baseline Failure
- [ ] Load large model with standard transformers
- [ ] Capture OOM error or slowness evidence
- [ ] Save error log / screenshot as proof

## Step 4 — AirLLM Inference
- [ ] Install airllm library
- [ ] Load large model with AirLLM (layer-by-layer)
- [ ] Run same test prompt
- [ ] Confirm valid response is returned
- [ ] Monitor and log RAM usage during inference

## Step 5 — Measurement and Comparison
- [ ] Measure peak RAM for each method
- [ ] Measure peak VRAM for each method
- [ ] Measure time to first token
- [ ] Measure total response time and tokens/sec
- [ ] Build comparison table
- [ ] Write latency vs memory tradeoff discussion

## Final
- [ ] Clean up notebook / script, add clear output cells
- [ ] Make sure no token or secret is exposed
- [ ] Review against PRD success criteria
- [ ] Submit
