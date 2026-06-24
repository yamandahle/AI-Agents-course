# PRD — HW5: AirLLM Evaluation Pipeline
**Version:** 1.0.0
**Author:** Nagham (naghammnsor@gmail.com)
**Date:** 2026-06-22
**Status:** Approved — Implementation Ready

---

## 1. Project Overview & Context

### 1.1 Background

Large Language Models (LLMs) have grown beyond the memory capacity of typical consumer
hardware. A 13-billion-parameter model in full FP32 precision requires ~52 GB of VRAM,
far exceeding even high-end prosumer GPUs. Two competing strategies address this:

- **Ollama** — quantize the model weights ahead-of-time (GGUF format) and run via a
  local server that automatically manages VRAM paging.
- **AirLLM** — stream individual transformer layers from disk on demand, never
  materializing the full model in memory, enabling ≥70B models on a single 8 GB GPU.

This project produces a **reproducible scientific evaluation pipeline** that measures
both strategies across three quantization bit-widths (Q2, Q4, Q8) on two models of
different scale, generating publication-quality trade-off visualizations.

### 1.2 Assignment Context

HW5 for Dr. Segal's AI Agents course (Lecture 08). Graded on:
- Correct AirLLM usage and layer-streaming demonstration
- Quantization impact analysis
- AI-agent-orchestrated modular architecture
- Report depth (theory + experiments + original ideas)
- Professional software standards (submission guidelines v3.00)

---

## 2. Problem Statement

**User Problem:** Running state-of-the-art LLMs locally is blocked by VRAM constraints.
Practitioners must choose between multiple memory-management strategies with no
systematic data on the quality/speed/memory trade-off surface.

**Research Question:** Across Ollama and AirLLM, and across Q2/Q4/Q8 quantization,
which (framework, quantization) combination yields the best tokens/sec per GB of RAM,
and how does output quality degrade with aggressive quantization?

---

## 3. Target Audience

| Stakeholder | Need |
|-------------|------|
| Course grader | Evidence of AirLLM mastery, modular code, agent-orchestrated prompts |
| ML practitioner | Reproducible benchmark to choose local LLM strategy |
| Researcher | Trade-off surface data for citation in future work |
| Self | Understanding of OS-level memory management for LLM inference |

---

## 4. Measurable Goals & KPIs

| KPI | Target |
|-----|--------|
| Pipeline runs end-to-end without crash | 100% |
| Evaluation matrix coverage | 2 models × 2 frameworks × 3 quant = 12 cells |
| Metrics captured per cell | ≥8 (see §7) |
| VRAM spike detection accuracy | ±50 MB tolerance |
| Plot generation time | <10 s after last experiment cell |
| Test coverage | ≥85% |
| Ruff lint violations | 0 |
| Files exceeding 150 lines | 0 |

---

## 5. User Stories

- **US-01:** As a researcher, I can swap in any HuggingFace model by editing one config
  line, so the pipeline is not hard-coded to specific weights.
- **US-02:** As a grader, I can run `python main.py --mode full` and get all 12 cells
  measured + plots saved without manual intervention.
- **US-03:** As an engineer, I can add a new quantization level (e.g. Q6) by adding
  one entry to the quantization config, without touching runner code.
- **US-04:** As a student, I can see a 3–4 sentence auto-generated summary alongside
  each plot that interprets the key finding.
- **US-05:** As a hardware-limited user, I can run only a subset of cells (e.g. AirLLM
  only) using a `--frameworks airllm` flag.
- **US-06:** As a developer, I can view real-time OS metrics (CPU %, RAM MB, VRAM MB)
  in a terminal-streamed table during inference.
- **US-07:** As a researcher, I can export all raw metrics to JSON and CSV for
  downstream analysis in R or Excel.

---

## 6. Functional Requirements

### 6.1 Model Registry (Hook Layer)

- FR-01: A `ModelRegistry` class reads `config/models.json` to resolve model IDs.
- FR-02: Each model entry specifies: HuggingFace repo ID, local cache path, size class
  (small/large), and per-framework compatibility flags.
- FR-03: The registry exposes `get_model(name)` and `list_models()` SDK methods.
- FR-04: No model ID is hard-coded outside `config/models.json`.

### 6.2 Framework Runners

- FR-05: `OllamaRunner` wraps the Ollama Python SDK. It starts/stops the local server,
  loads a model in the requested quantization, runs inference, and returns metrics.
- FR-06: `AirLLMRunner` uses the `airllm` library. It initializes a
  `AirLLMAuto.from_pretrained()` instance with `compression=<quant>`, runs forward
  passes, and returns metrics.
- FR-07: Both runners expose a common `RunnerProtocol` interface:
  `load(model, quant)`, `infer(prompt)` → `InferenceResult`, `unload()`.
- FR-08: Both runners emit timing events: `load_start`, `load_end`, `first_token`,
  `generation_end`.

### 6.3 Quantization

- FR-09: Quantization levels supported: Q2, Q4, Q8 (integer bit-width).
- FR-10: For Ollama: quantization is expressed as GGUF model tags (e.g. `q4_K_M`).
- FR-11: For AirLLM: quantization maps to `compression` parameter values.
- FR-12: A `QuantizationConfig` dataclass validates bit-width ∈ {2, 4, 8} at startup.
- FR-13: Adding a new quantization level requires only a config file edit.

### 6.4 OS Page Monitoring

- FR-14: A `SystemMonitor` class runs in a background thread, sampling every 500 ms.
- FR-15: Metrics captured per sample:
  - CPU utilization (%) — via `psutil.cpu_percent()`
  - RAM used (MB) — via `psutil.virtual_memory().used`
  - Swap used (MB) — via `psutil.swap_memory().used`
  - VRAM allocated (MB) — via `pynvml` or `torch.cuda.memory_allocated()`
  - Disk I/O read bytes — via `psutil.disk_io_counters()`
- FR-16: VRAM spike detection: when VRAM increases by >500 MB in a single sample
  interval, a `VRAMSpikeEvent` is emitted and logged.
- FR-17: All samples are stored in a `MetricsBuffer` (thread-safe deque).
- FR-18: Monitor starts before model load and stops after model unload, capturing the
  full lifecycle.

### 6.5 Evaluation Loop

- FR-19: `EvaluationLoop` iterates over the Cartesian product of models × frameworks
  × quantization levels.
- FR-20: For each cell: start monitor → load model → run inference → stop monitor →
  collect metrics → store result.
- FR-21: Results are persisted to `results/<timestamp>/cell_<model>_<fw>_<quant>.json`
  after each cell so partial runs are recoverable.
- FR-22: A `--resume` flag skips cells whose result JSON already exists.
- FR-23: The loop emits a progress bar via `rich` showing completed/total cells.

### 6.6 Visualization & Summary

- FR-24: Four plots are generated post-evaluation:
  1. **Heatmap** — tokens/sec by (framework, quantization), one subplot per model.
  2. **Line chart** — RAM over time for each cell, overlaid with framework color.
  3. **Bar chart** — Peak VRAM by (model, framework, quantization).
  4. **Scatter** — RAM usage vs. tokens/sec trade-off, colored by framework.
- FR-25: Each plot is saved as PNG (300 DPI) and SVG to `assets/`.
- FR-26: A `SummaryGenerator` produces a 3–4 sentence narrative per plot using
  rule-based logic (no LLM call required for summary).
- FR-27: A combined `report.html` is generated with all four plots inline plus
  summaries.

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Modularity | Max 150 lines per file; SDK single entry point |
| Reproducibility | Random seed fixed; config fully externalized |
| Portability | CPU-only fallback when no CUDA GPU detected |
| Observability | Structured JSON log per experiment cell |
| Safety | API gatekeeper wraps all HuggingFace download calls |
| Style | Ruff: zero violations; black-formatted |
| Docs | Every public function has a one-line docstring |
| Tests | ≥85% line coverage via pytest |
| Dependencies | Managed via uv; pinned in uv.lock |
| Secrets | No tokens in code; loaded from `.env` via python-dotenv |

---

## 8. Assumptions & Constraints

- **Hardware assumption:** The machine running the pipeline has at least 16 GB RAM and
  optionally a CUDA GPU. CPU-only mode is slower but functional.
- **Ollama assumption:** Ollama is installed and accessible at `localhost:11434`.
- **AirLLM assumption:** The `airllm` package supports the chosen model architectures.
- **Constraint:** Models are not distributed with the project; they are downloaded on
  first run per the model registry config.
- **Out of scope:** Multi-GPU setups, distributed inference, fine-tuning, training.

---

## 9. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `airllm` | ≥0.9.0 | Layer-streaming inference |
| `ollama` | ≥0.2.0 | Ollama Python SDK |
| `psutil` | ≥5.9.0 | CPU/RAM/Swap metrics |
| `pynvml` | ≥11.0.0 | NVIDIA VRAM metrics |
| `torch` | ≥2.2.0 | GPU tensor allocation queries |
| `transformers` | ≥4.40.0 | HuggingFace model loading |
| `matplotlib` | ≥3.8.0 | Plot generation |
| `seaborn` | ≥0.13.0 | Heatmap styling |
| `rich` | ≥13.0.0 | Progress bars, live tables |
| `python-dotenv` | ≥1.0.0 | Secrets from .env |
| `pytest` | ≥8.0.0 | Test runner |
| `ruff` | ≥0.4.0 | Linter |

---

## 10. Timeline & Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| M0 — Docs approved | 2026-06-22 | PRD, PLAN, TODO signed off |
| M1 — Infrastructure | 2026-06-24 | SDK, config, gatekeeper, monitor |
| M2 — Runners | 2026-06-26 | Ollama + AirLLM runners passing unit tests |
| M3 — Eval loop | 2026-06-28 | Full 12-cell loop runs on CPU |
| M4 — Plots | 2026-06-29 | All 4 plots + summaries generated |
| M5 — Tests | 2026-06-30 | ≥85% coverage, 0 Ruff violations |
| M6 — Report | 2026-07-01 | Final report.md + notebook submitted |

---

## 11. Success Criteria (Acceptance Criteria)

- AC-01: `python main.py --mode full` completes all 12 cells without exception.
- AC-02: All four plots are saved to `assets/` with correct labels and color coding.
- AC-03: `results/` contains one JSON file per completed cell.
- AC-04: `pytest --cov=src --cov-report=term-missing` reports ≥85% coverage.
- AC-05: `ruff check src/` reports 0 violations.
- AC-06: No file in `src/` exceeds 150 lines.
- AC-07: `report.html` renders correctly in a browser with all plots and summaries.
- AC-08: The model registry is hookable — adding a third model requires only a config edit.
