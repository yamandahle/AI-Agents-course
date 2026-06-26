# PRD — AirLLM Homework (HW5)

## Goal
Prove that AirLLM enables running large language models locally that would not normally fit in GPU VRAM or system RAM, by using OS virtual memory (mmap + paging) to process the model layer by layer.

## Background
Standard local inference loads the entire model into VRAM at once. For models like LLaMA-70B this is impossible on consumer hardware. AirLLM solves this by loading one layer at a time, leveraging the OS paging system so the model never fully resides in memory simultaneously.

## Deliverables
- Python scripts for all 10 steps (each under 150 lines)
- Measured comparison table: RAM, VRAM, response time, tokens/sec across GPU vs AirLLM CPU
- Evidence of the "too big" failure (OOM error or crash log)
- Evidence of AirLLM success on the same model
- Economic analysis: on-prem vs cloud API break-even
- TTFT & TPOT measurement with prefill/decode explanation
- Quantization level comparison: FP32 / INT8 / INT4
- Unified dashboard chart and scaling projection (original extension)
- README with screenshots, JSON result links, and charts for every step

## Success Criteria
1. Ollama runs phi3:mini locally and returns a valid response
2. huggyllama/llama-13b fails (OOM) under standard loading on T4 GPU
3. The same model produces a valid response via AirLLM on CPU (peak RAM ~2.42 GB)
4. Metrics are recorded and the latency vs memory tradeoff is clearly discussed
5. Economic analysis shows when on-prem is cheaper than API
6. TTFT and TPOT are measured and the prefill/decode distinction is explained
7. Three quantization levels benchmarked with compression ratios and error metrics
8. Original extension demonstrates AirLLM's growing advantage at larger model sizes

## Constraints
- Use a virtual environment (venv), recommended tool: uv
- Do not use the latest Python version (library compatibility issues)
- Keep the Hugging Face token out of any committed file
- Start with Q2 quantization just to verify the pipeline, upgrade quality later
- Allocate sufficient disk space before downloading large models
- Submission format: Jupyter notebook (.ipynb) or Python scripts with clear output
