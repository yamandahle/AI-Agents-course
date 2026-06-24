# PRD — AirLLM Homework (HW5)

## Goal
Prove that AirLLM enables running large language models locally that would not normally fit in GPU VRAM or system RAM, by using OS virtual memory (mmap + paging) to process the model layer by layer.

## Background
Standard local inference loads the entire model into VRAM at once. For models like LLaMA-70B this is impossible on consumer hardware. AirLLM solves this by loading one layer at a time, leveraging the OS paging system so the model never fully resides in memory simultaneously.

## Deliverables
- A working Python script (or Jupyter notebook) that runs all 5 steps end-to-end
- Measured comparison table: RAM, VRAM, response time, tokens/sec across GPU vs AirLLM CPU
- Evidence of the "too big" failure (OOM error or crash log)
- Evidence of AirLLM success on the same model

## Success Criteria
1. Ollama runs a small model locally and returns a valid response
2. A large model fails (OOM / crash) under normal loading
3. The same large model produces a valid response via AirLLM
4. Metrics are recorded and the latency vs memory tradeoff is clearly discussed

## Constraints
- Use a virtual environment (venv), recommended tool: uv
- Do not use the latest Python version (library compatibility issues)
- Keep the Hugging Face token out of any committed file
- Start with Q2 quantization just to verify the pipeline, upgrade quality later
- Allocate sufficient disk space before downloading large models
- Submission format: Jupyter notebook (.ipynb) or Python scripts with clear output
