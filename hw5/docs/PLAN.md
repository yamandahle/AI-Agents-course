# PLAN — AirLLM Homework (HW5)

## Step 1 — Choose Task and Model
- Task: simple text generation (question answering)
- Pick a small model for baseline (e.g. LLaMA-3-8B or similar, fits in RAM)
- Pick a large model for the AirLLM demo (e.g. LLaMA-3-70B or Mistral-large)
- Check: license (must allow local use), format (SafeTensors preferred), VRAM requirement
- Download models from Hugging Face (requires HF account + token)

## Step 2 — Install Ollama and Run Basic Inference
- Install Ollama on the machine
- Pull a small GGUF model: `ollama pull llama3`
- Run a test prompt and confirm a valid response is returned
- This validates the on-prem setup is working before moving to harder steps

## Step 3 — Baseline: Attempt to Load a Too-Large Model Normally
- Choose a model clearly too big for available VRAM/RAM (e.g. 70B at FP16)
- Attempt to load it with standard transformers / PyTorch
- Capture the OOM error or crash output as evidence
- Log: VRAM attempted, RAM attempted, error message

## Step 4 — AirLLM: Run the Same Large Model on CPU
- Install AirLLM library
- Load the same large model using AirLLM (layer-by-layer, mmap-backed)
- Run the same test prompt
- Confirm a valid response is returned
- Log: RAM usage during inference, response received

## Step 5 — Measure and Compare
- Metrics to record for each method:
  - Peak RAM usage (MB)
  - Peak VRAM usage (MB)
  - Time to first token (seconds)
  - Total response time (seconds)
  - Tokens per second
- Build a comparison table: Normal GPU load vs AirLLM CPU
- Write a short discussion on the latency vs memory tradeoff

## Environment Setup
- Python version: 3.10 or 3.11 (avoid 3.13+)
- Virtual environment: `uv venv` or `python -m venv .venv`
- Key dependencies: `transformers`, `torch`, `airllm`, `ollama`, `psutil`, `pynvml`
