# PLAN — HW5: AirLLM Evaluation Pipeline
**Version:** 1.0.0
**Author:** Nagham (naghammnsor@gmail.com)
**Date:** 2026-06-22
**Status:** Approved

---

## 1. Architecture Overview (C4 — Context Level)

```
┌─────────────────────────────────────────────────────────────┐
│                    HW5 Evaluation System                    │
│                                                             │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  User /  │───▶│   main.py CLI    │───▶│  SDK Layer   │  │
│  │  Grader  │    │  (entry point)   │    │  (sdk.py)    │  │
│  └──────────┘    └──────────────────┘    └──────┬───────┘  │
│                                                 │           │
│  ┌──────────────────────────────────────────────┼─────────┐ │
│  │              Services Layer                  │         │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────▼──────┐  │ │
│  │  │ModelRegistry│  │EvaluationLoop│  │SystemMonitor │  │ │
│  │  └─────────────┘  └──────┬───────┘  └──────────────┘  │ │
│  │                          │                             │ │
│  │  ┌───────────────────────▼───────────────────────────┐ │ │
│  │  │              Runner Protocol                       │ │ │
│  │  │  ┌──────────────┐        ┌──────────────────────┐ │ │ │
│  │  │  │ OllamaRunner │        │   AirLLMRunner       │ │ │ │
│  │  │  └──────────────┘        └──────────────────────┘ │ │ │
│  │  └───────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Infrastructure  │  │  Plotter     │  │  Gatekeeper  │  │
│  │  (HF Hub, Ollama │  │  (matplotlib)│  │  (rate limit)│  │
│  │   disk, NVML)    │  └──────────────┘  └──────────────┘  │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Container Diagram (C4 — Container Level)

```
                        ┌─────────────────┐
                        │   main.py CLI   │
                        │  ─────────────  │
                        │  Python 3.12    │
                        │  entry point    │
                        └────────┬────────┘
                                 │ calls
                                 ▼
                        ┌─────────────────┐
                        │    SDK Layer    │
                        │  sdk/sdk.py     │
                        │  Single API for │
                        │  all consumers  │
                        └────────┬────────┘
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
   ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
   │  EvaluationLoop  │  │ SystemMonitor│  │ ModelRegistry│
   │  services/       │  │ services/    │  │ services/    │
   │  eval_loop.py    │  │ monitor.py   │  │ model_reg.py │
   └────────┬─────────┘  └──────────────┘  └──────────────┘
            │
    ┌───────┴────────┐
    ▼                ▼
┌──────────┐  ┌────────────┐
│ Ollama   │  │  AirLLM   │
│ Runner   │  │  Runner   │
│ ollama_  │  │  airllm_  │
│ runner.py│  │  runner.py│
└──────┬───┘  └─────┬──────┘
       │             │
       ▼             ▼
┌──────────┐  ┌────────────────────────────┐
│ Ollama   │  │  HuggingFace Hub           │
│ Server   │  │  (weights downloaded to    │
│ :11434   │  │   ~/.cache/huggingface/)   │
└──────────┘  └────────────────────────────┘
```

---

## 3. Component Diagram (C4 — Component Level)

### 3.1 SDK Layer (`src/hw5/sdk/sdk.py`)

```
┌─────────────────────────────────────┐
│           EvalPipelineSDK           │
│─────────────────────────────────────│
│ + run_full_evaluation()             │
│ + run_single_cell(model, fw, quant) │
│ + list_models()                     │
│ + get_results()                     │
│ + generate_plots()                  │
│ + generate_report()                 │
└─────────────────────────────────────┘
```

### 3.2 Services Layer

```
ModelRegistry          EvaluationLoop        SystemMonitor
────────────           ──────────────        ─────────────
+ load_config()        + run()               + start()
+ get_model(name)      + run_cell()          + stop()
+ list_models()        + resume()            + get_samples()
+ validate()           + save_result()       + get_peak()
                       + iter_cells()        + detect_spikes()

OllamaRunner           AirLLMRunner          Plotter
────────────           ────────────          ───────
+ load(model,quant)    + load(model,quant)   + heatmap()
+ infer(prompt)        + infer(prompt)       + timeline()
+ unload()             + unload()            + bar_chart()
+ health_check()       + health_check()      + scatter()
                                             + save_all()
                                             + to_html()
```

### 3.3 Shared Layer

```
ApiGatekeeper          Config                QuantizationConfig
─────────────          ──────                ──────────────────
+ execute(fn, *args)   + load()              + validate(bits)
+ set_rate(rps)        + get(key, default)   + to_ollama_tag()
+ __enter__/__exit__   + require(key)        + to_airllm_param()
```

---

## 4. Data Flow Diagram

```
models.json ──▶ ModelRegistry
config/
setup.json  ──▶ Config
rate_limits.json ──▶ ApiGatekeeper

                 ┌──────────────┐
CLI args ───────▶│ EvalPipelineSDK │
                 └──────┬───────┘
                        │ iter_cells()
                        ▼
                 ┌──────────────┐
                 │EvaluationLoop│
                 │  for each    │──── SystemMonitor.start()
                 │  (m, fw, q)  │
                 │              │──── Runner.load(m, q)
                 │              │──── Runner.infer(prompt)
                 │              │──── Runner.unload()
                 │              │──── SystemMonitor.stop()
                 └──────┬───────┘
                        │
                        ▼
               results/<ts>/
               cell_<m>_<fw>_<q>.json
                        │
                        ▼
                 ┌──────────────┐
                 │   Plotter    │────▶ assets/*.png, *.svg
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │SummaryGenera-│────▶ assets/summary_*.txt
                 │     tor      │
                 └──────┬───────┘
                        │
                        ▼
                   report.html
```

---

## 5. Evaluation Matrix

The pipeline executes a full Cartesian product:

```
Models (M):        [model_a, model_b]          ← hookable via config
Frameworks (F):    [ollama, airllm]
Quantization (Q):  [Q2, Q4, Q8]

Total cells: |M| × |F| × |Q| = 2 × 2 × 3 = 12
```

### Execution Order (resource-safe)

Cells run in this order to minimize GPU thrash:
```
1.  (model_a, ollama,  Q4)   ← warm-up with stable mid-precision
2.  (model_a, ollama,  Q8)
3.  (model_a, ollama,  Q2)
4.  (model_a, airllm,  Q4)
5.  (model_a, airllm,  Q8)
6.  (model_a, airllm,  Q2)
7.  (model_b, ollama,  Q4)
8.  (model_b, ollama,  Q8)
9.  (model_b, ollama,  Q2)
10. (model_b, airllm,  Q4)
11. (model_b, airllm,  Q8)
12. (model_b, airllm,  Q2)
```

---

## 6. OS Page Monitoring Architecture

```
Main Thread                    Monitor Thread (daemon)
───────────                    ──────────────────────
monitor.start()          ──▶  while not stop_event.set():
                               │  sample = {
                               │    ts:    time.perf_counter()
                               │    cpu:   psutil.cpu_percent()
                               │    ram:   psutil.virtual_memory().used
                               │    swap:  psutil.swap_memory().used
                               │    vram:  pynvml.nvmlDeviceGetMemoryInfo()
                               │    disk:  psutil.disk_io_counters()
                               │  }
                               │  buffer.append(sample)
                               │  if vram_spike(sample):
                               │      spike_log.append(sample)
                               │  time.sleep(0.5)

monitor.stop()           ──▶  stop_event.set()
                              return MetricsSnapshot(buffer, spike_log)
```

### VRAM Spike Detection Rule

```python
SPIKE_THRESHOLD_MB = 500  # configurable

def vram_spike(prev_sample, curr_sample) -> bool:
    delta = curr_sample["vram"] - prev_sample["vram"]
    return delta > SPIKE_THRESHOLD_MB
```

### CPU Fallback

When no CUDA GPU is detected:
- VRAM metrics = 0 (not N/A, so plots still render)
- A `cpu_only=True` flag is stored in each cell result
- Plots annotate CPU-only cells with a dashed border

---

## 7. Module File Map

```
src/hw5/
├── __init__.py
├── sdk/
│   ├── __init__.py
│   └── sdk.py              ← EvalPipelineSDK (public API)
├── services/
│   ├── __init__.py
│   ├── model_registry.py   ← ModelRegistry
│   ├── eval_loop.py        ← EvaluationLoop + CellResult
│   ├── ollama_runner.py    ← OllamaRunner
│   ├── airllm_runner.py    ← AirLLMRunner
│   ├── runner_protocol.py  ← RunnerProtocol (ABC)
│   ├── monitor.py          ← SystemMonitor + MetricsBuffer
│   ├── plotter.py          ← Plotter (heatmap, line, bar, scatter)
│   └── summary.py          ← SummaryGenerator
├── shared/
│   ├── __init__.py
│   ├── gatekeeper.py       ← ApiGatekeeper
│   ├── config.py           ← Config loader
│   ├── quant_config.py     ← QuantizationConfig
│   └── constants.py        ← SPIKE_THRESHOLD_MB, SAMPLE_INTERVAL_S, etc.
└── main.py                 ← CLI entry point (argparse)

tests/
├── unit/
│   ├── test_model_registry.py
│   ├── test_eval_loop.py
│   ├── test_ollama_runner.py
│   ├── test_airllm_runner.py
│   ├── test_monitor.py
│   ├── test_plotter.py
│   ├── test_summary.py
│   ├── test_gatekeeper.py
│   ├── test_config.py
│   └── test_quant_config.py
└── integration/
    ├── test_ollama_integration.py
    └── test_airllm_integration.py

config/
├── models.json             ← Model registry (hookable)
├── setup.json              ← Evaluation parameters
└── rate_limits.json        ← ApiGatekeeper limits

docs/
├── PRD.md
├── PLAN.md
├── TODO.md
├── PRD_airllm.md
├── PRD_quantization.md
└── PRD_monitoring.md

assets/                     ← Generated plots (.png, .svg)
results/                    ← Per-cell JSON results
notebooks/                  ← Jupyter exploration notebooks
```

---

## 8. Architectural Decision Records (ADRs)

### ADR-01: Protocol over Inheritance for Runners

**Decision:** `RunnerProtocol` uses `typing.Protocol` (structural subtyping) rather
than an ABC base class.

**Rationale:** Allows third-party runner wrappers (e.g. llama.cpp via subprocess) to
satisfy the protocol without inheriting from our class, reducing coupling.

**Trade-off:** Type errors only caught at static-analysis time (mypy), not at runtime.

**Accepted risk:** The test suite mocks both runner types, catching mismatches early.

---

### ADR-02: Background Thread for Monitor, Not Async

**Decision:** `SystemMonitor` uses `threading.Thread`, not `asyncio`.

**Rationale:** `psutil` and `pynvml` are synchronous C-extension calls; wrapping them
in asyncio executors adds overhead without benefit. The inference runners themselves
are synchronous (LLM forward passes block the GIL anyway).

**Trade-off:** Cannot `await` monitor events; spike callbacks are delivered via a
thread-safe queue checked on the main thread.

---

### ADR-03: Rule-Based Summary, Not LLM-Generated

**Decision:** `SummaryGenerator` uses threshold comparisons on collected metrics to
produce 3–4 sentences, not an LLM.

**Rationale:** The pipeline already saturates local resources during evaluation; adding
an LLM call for summary generation would require either a remote API (latency, cost,
secrets) or a second local load (VRAM conflict). Rule-based logic is deterministic and
reproducible.

**Trade-off:** Summaries are less fluent. Mitigated by carefully written templates.

---

### ADR-04: uv for Dependency Management

**Decision:** All dependencies managed via `uv` with a pinned `uv.lock`.

**Rationale:** Submission guidelines v3.00 §8 mandate uv. Lock file ensures
reproducible environments across machines.

---

### ADR-05: Results Persisted Per Cell, Not at End

**Decision:** Each experiment cell is written to disk immediately after completion.

**Rationale:** A 12-cell run on large models may take 30–90 minutes. If the process
crashes at cell 11, no data is lost. The `--resume` flag re-reads existing JSONs to
skip completed cells.

---

## 9. API Contracts

### RunnerProtocol

```python
class RunnerProtocol(Protocol):
    def load(self, model_id: str, quant: QuantizationConfig) -> None: ...
    def infer(self, prompt: str) -> InferenceResult: ...
    def unload(self) -> None: ...
    def health_check(self) -> bool: ...
```

### InferenceResult (dataclass)

```python
@dataclass
class InferenceResult:
    output_text: str
    tokens_generated: int
    total_time_s: float
    first_token_latency_s: float
    tokens_per_sec: float
    framework: str
    model_id: str
    quant: str
```

### CellResult (dataclass)

```python
@dataclass
class CellResult:
    inference: InferenceResult
    metrics: MetricsSnapshot
    cell_id: str          # e.g. "model_a__ollama__Q4"
    started_at: str       # ISO 8601
    finished_at: str
    cpu_only: bool
```

### MetricsSnapshot

```python
@dataclass
class MetricsSnapshot:
    samples: list[dict]   # raw per-sample dicts
    spike_events: list[dict]
    peak_ram_mb: float
    peak_vram_mb: float
    peak_swap_mb: float
    avg_cpu_pct: float
    total_disk_read_mb: float
```

---

## 10. Plot Specifications

### Plot 1 — Heatmap: Tokens/sec

- X-axis: Quantization (Q2, Q4, Q8)
- Y-axis: Framework (Ollama, AirLLM)
- Value: mean tokens/sec
- One subplot per model
- Color scale: RdYlGn (red=slow, green=fast)
- Annotate each cell with exact value

### Plot 2 — RAM Timeline

- X-axis: time (seconds from load_start)
- Y-axis: RAM used (MB)
- One line per cell (model_fw_quant)
- Color: framework (Ollama=blue, AirLLM=orange)
- Linestyle: quantization (Q2=dotted, Q4=solid, Q8=dashed)
- Vertical markers at load_end and first_token

### Plot 3 — Peak VRAM Bar Chart

- X-axis: (model, quant) combinations grouped by model
- Y-axis: Peak VRAM (MB)
- Color: framework (Ollama=steelblue, AirLLM=darkorange)
- Error bars: ±1 std if multiple runs

### Plot 4 — Trade-off Scatter

- X-axis: Peak RAM (MB) (proxy for memory pressure)
- Y-axis: Tokens/sec
- Each point = one cell
- Color: framework
- Marker shape: quantization (Q2=triangle, Q4=circle, Q8=square)
- Annotate Pareto-optimal points

---

## 11. Configuration Schema

### `config/models.json`

```json
{
  "models": [
    {
      "name": "model_a",
      "hf_repo_id": "<HOOK: replace with HuggingFace repo ID>",
      "local_cache": "~/.cache/huggingface/hub",
      "size_class": "large",
      "ollama_compatible": true,
      "airllm_compatible": true,
      "description": "First model - larger size"
    },
    {
      "name": "model_b",
      "hf_repo_id": "<HOOK: replace with HuggingFace repo ID>",
      "local_cache": "~/.cache/huggingface/hub",
      "size_class": "small",
      "ollama_compatible": true,
      "airllm_compatible": true,
      "description": "Second model - smaller size"
    }
  ]
}
```

### `config/setup.json`

```json
{
  "quantization_levels": ["Q2", "Q4", "Q8"],
  "frameworks": ["ollama", "airllm"],
  "eval_prompt": "Explain the concept of virtual memory in operating systems in 3 sentences.",
  "max_tokens": 200,
  "monitor_interval_s": 0.5,
  "vram_spike_threshold_mb": 500,
  "ollama_host": "http://localhost:11434",
  "resume": false,
  "results_dir": "results",
  "assets_dir": "assets"
}
```

---

## 12. Test Strategy

| Layer | Tool | Target Coverage |
|-------|------|----------------|
| Unit — services | pytest + unittest.mock | ≥90% |
| Unit — shared | pytest | ≥95% |
| Integration — Ollama | pytest (requires Ollama installed) | smoke test |
| Integration — AirLLM | pytest (requires model cache) | smoke test |
| Lint | ruff check src/ | 0 violations |
| Type check | mypy src/ | 0 errors (strict=False) |

Integration tests are marked `@pytest.mark.integration` and skipped in CI unless
`INTEGRATION=1` env var is set.

---

## 13. Deployment Notes

The pipeline is a CLI tool, not a server. "Deployment" means:

1. Clone repo
2. `uv sync` — resolves dependencies from uv.lock
3. Copy `.env-example` → `.env`, fill in HF_TOKEN
4. Edit `config/models.json` with desired HuggingFace model IDs
5. Run: `uv run python src/hw5/main.py --mode full`
6. View results in `results/` and plots in `assets/`
7. Open `report.html` in browser

CPU-only machines: same steps, VRAM metrics will show 0, plots still render correctly.
