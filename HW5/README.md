# HW5 — AirLLM Evaluation Pipeline

![Python](https://img.shields.io/badge/python-3.12-blue)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
![Ruff](https://img.shields.io/badge/ruff-0%20violations-brightgreen)
![Tests](https://img.shields.io/badge/tests-270%20passed-brightgreen)

A structured scientific evaluation of **AirLLM** vs **Ollama** across 3 quantization
levels (Q2, Q4, Q8) on 2 models of different sizes.  
Course: AI Agents · Dr. Segal · Assignment 5 · 2026-06-22

---

## Hardware Specs

| Component | Value |
|-----------|-------|
| CPU | Intel i7-1165G7 @ 2.80 GHz (8 threads) |
| RAM | ~7.6 GB (WSL2) |
| GPU | None — CPU-only mode |
| OS | Linux WSL2 (Windows 11 host) |
| Python | 3.12 |

---

## Installation

### 1. Install uv (package manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install dependencies
```bash
git clone <repo-url>
cd HW5
uv sync
```

### 3. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &   # start server in background
```

### 4. Configure secrets
```bash
cp .env-example .env
# Edit .env: add your HuggingFace token (only needed for gated models like Llama-3)
```

### 5. Set your models (optional — defaults are pre-configured)
Edit `config/models.json` to change which HuggingFace models are used.  
The two default models are `Qwen/Qwen2.5-7B-Instruct` and `Qwen/Qwen2.5-1.5B-Instruct`.

---

## Usage

### Run the full evaluation (all 12 cells)
```bash
uv run python src/hw5/main.py --mode full
```

### Run a single cell
```bash
uv run python src/hw5/main.py --mode full --cell model_a__ollama__Q4
```

### Dry-run (print cells without executing)
```bash
uv run python src/hw5/main.py --mode full --dry-run
```

### Generate plots only (from existing results)
```bash
uv run python src/hw5/main.py --mode plot
```

### Generate HTML report
```bash
uv run python src/hw5/main.py --mode report
```

### Filter by framework or quantization
```bash
uv run python src/hw5/main.py --frameworks airllm --quants Q4,Q8
```

### Resume an interrupted run
```bash
uv run python src/hw5/main.py --mode full --resume
```

---

## Configuration Guide

| File | Purpose |
|------|---------|
| `config/models.json` | Model registry — swap models here (no code changes needed) |
| `config/setup.json` | Eval parameters: prompt, max tokens, monitor interval |
| `config/rate_limits.json` | ApiGatekeeper rate limits for HF downloads and inference |
| `.env` | Secrets: HF_TOKEN, OLLAMA_HOST |

**To add a model:** append an entry to the `models` array in `config/models.json`.  
Fields: `name`, `hf_repo_id`, `ollama_tag`, `size_class` (`"small"` or `"large"`),
`ollama_compatible`, `airllm_compatible`.

---

## Expected Output

After a full run, you will find:
```
results/<timestamp>/
    cell_model_a__ollama__Q4.json
    cell_model_a__ollama__Q8.json
    ... (12 files total)

assets/
    heatmap.png / heatmap.svg
    ram_timeline.png / ram_timeline.svg
    vram_bar.png / vram_bar.svg
    tradeoff_scatter.png / tradeoff_scatter.svg
    report.html
```

Open `assets/report.html` in your browser to view all plots and auto-generated summaries.

---

## Running Tests

```bash
# Unit tests only
make test

# Full suite including integration (requires Ollama + models)
make test-all

# Lint + format check + file-length audit
make lint

# Type check
make type-check
```

Test markers:
- `@pytest.mark.integration` — requires Ollama or HuggingFace model cache
- `@pytest.mark.slow` — takes >30 seconds

---

## Troubleshooting

**`ConnectionRefusedError: Ollama not reachable`**  
→ Start Ollama: `ollama serve`

**`RegistryError: HOOK placeholder detected`**  
→ Edit `config/models.json` and replace any `<HOOK>` placeholders with real values

**`OOMError` on Q8 7B model**  
→ Your RAM is too limited for Q8 on a 7B model. Use `--quants Q4,Q2` instead

**`ModuleNotFoundError: airllm`**  
→ Run `uv sync` to install dependencies

**VRAM metrics all 0.0**  
→ Expected on CPU-only machines (no NVIDIA GPU detected)

---

## Contribution Guidelines

- Max 150 lines per Python file
- Run `make lint` before committing
- All new functions need a one-line docstring
- Tests go in `tests/unit/` (no external services) or `tests/integration/` (mark with `@pytest.mark.integration`)
- No secrets or model weights committed to git

---

## License & Credits

MIT License — see `LICENSE`

Libraries: airllm, ollama, psutil, pynvml, transformers, torch, matplotlib, seaborn, pandas, rich, python-dotenv, huggingface-hub
