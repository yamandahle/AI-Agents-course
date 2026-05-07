# Technical Development Plan — HW1: Signal Reconstruction

## 1. Primary Constraints & Standards
- **Sampling Rate:** 1000 Hz (strict requirement)
- **File Limit:** Every source file MUST be under 150 lines
- **Context Window:** 10-sample sliding window (default W=10, experiments: W=5, W=10, W=20)
- **Package Manager:** `uv` only — no pip
- **Config:** All parameters in `configs/*.json` — nothing hardcoded in source
- **Seed:** 42 for all random operations

---

## 2. Mathematical Foundations

### Signal Generation
```
clean:  y(t) = A * sin(2π * f * t + phase)
noisy:  y_noisy(t) = (A + alpha*σ) * sin(2π * f * t + phase + beta*σ)
        σ ~ N(0,1), re-sampled fresh for every window
```

### Model State Logic (RNN/LSTM)
```
y_t = f_w(x_t, h_{t-1})   where h is the hidden memory state
```

---

## 3. Project Structure

```
hw1/
├── pyproject.toml               (uv-managed, all deps declared here)
├── .python-version              (3.11)
├── .gitignore
│
├── configs/                     (all parameters — nothing hardcoded)
│   ├── signals.json             (frequencies, amplitude, phase, duration, sample_rate)
│   ├── noise.json               (low/med/high alpha+beta presets)
│   ├── training.json            (epochs, batch_size, lr, window_sizes, train_ratio, seed)
│   └── models.json              (hidden_size, num_layers, fc_hidden)
│
├── docs/
│   ├── PRD.md   ✅
│   ├── PLAN.md  ✅  (this file)
│   └── TODO.md
│
├── src/
│   ├── sdk/
│   │   ├── __init__.py          (exports HW1SDK)
│   │   ├── hw1_sdk.py           (HW1SDK — single entry point for all logic)
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── base.py          (BaseModel: abstract fit/predict/save/load)
│   │       ├── mlp.py    ✅*    (fix: output W samples, not 1)
│   │       ├── rnn.py    ✅*    (fix: one_hot→h0, output W samples)
│   │       └── lstm.py   ✅*    (fix: one_hot→h0+c0, output W samples)
│   │
│   └── services/
│       ├── __init__.py
│       ├── data_generator.py ✅* (fix: add S5, one-hot size 5→ not 4)
│       ├── train.py          ✅* (fix: target is W samples not 1)
│       ├── research_visualizer.py ✅*
│       ├── experiment_runner.py   (135-run Cartesian product loop)
│       └── results_collector.py  (ExperimentResult + outputs/results/results.json)
│
├── tests/
│   ├── conftest.py              (shared fixtures: tiny_config, dummy_signal, tmp_dir)
│   ├── unit/
│   │   ├── test_signals.py
│   │   ├── test_models.py
│   │   └── test_trainer.py
│   └── integration/
│       ├── test_sdk.py
│       └── test_experiments.py
│
└── outputs/
    ├── .gitkeep
    ├── figures/                 (all .png plots)
    └── results/                 (results.json — 135 entries)
```
`✅` = already exists from Nagham's work &nbsp;&nbsp; `✅*` = exists but needs fixes

---

## 4. SDK Architecture

```
External Consumers (tests / main.py / notebooks)
                    |
                    v
             +------------+
             |  HW1SDK    |  ← single entry point for ALL operations
             +-----+------+
                   |
        +----------+----------+----------+
        v          v          v          v
   sdk/models/  services/  services/  services/
   (mlp, rnn,   data_gen   train.py   experiment
    lstm, base)  erator              _runner
                   |                    |
                   v                    v
              configs/*.json    outputs/results/
                                  results.json
```

---

## 5. Model Specifications

### MLP (Fully Connected)
```
Input:  (W+5,)  — concatenation of [one_hot(5,), noisy_window(W,)]
Linear(W+5, 256) → ReLU → Linear(256, 256) → ReLU → Linear(256, W)
Output: (W,)
```

### RNN
```
Input: noisy_window reshaped to (W, 1)
one_hot → Linear(5, 128) → h0  shape: (num_layers=2, batch, 128)
RNN(input_size=1, hidden_size=128, num_layers=2, batch_first=True)
last hidden state → Linear(128, W)
Output: (W,)
```

### LSTM
```
Same as RNN but uses both h0 and c0:
one_hot → Linear(5, 128) → h0 and c0
LSTM(input_size=1, hidden_size=128, num_layers=2, batch_first=True)
last output step → Linear(128, W)
Output: (W,)
```

---

## 6. Experiment Matrix

| Dimension   | Values                                                         |
|-------------|----------------------------------------------------------------|
| Signal      | S1 (1Hz), S2 (2Hz), S3 (5Hz), S4 (10Hz), S5 (sum of S1–S4)   |
| Noise level | low (α=0.05, β=0.05) · med (α=0.1, β=0.1) · high (α=0.3, β=0.3) |
| Window size | W=5, W=10, W=20                                                |
| Model       | MLP, RNN, LSTM                                                 |

**Total: 5 × 3 × 3 × 3 = 135 training runs**

Each run records: train loss history, validation loss history, best validation MSE, best epoch.
All saved to `outputs/results/results.json`.

---

## 7. Configuration Files

**configs/signals.json**
```json
{ "frequencies": [1, 2, 5, 10], "amplitude": 1.0, "phase": 0,
  "duration": 10, "sample_rate": 1000 }
```

**configs/noise.json**
```json
{ "low":  {"alpha": 0.05, "beta": 0.05},
  "med":  {"alpha": 0.1,  "beta": 0.1},
  "high": {"alpha": 0.3,  "beta": 0.3} }
```

**configs/training.json**
```json
{ "epochs": 50, "batch_size": 64, "lr": 0.001,
  "window_sizes": [5, 10, 20], "train_ratio": 0.8, "seed": 42 }
```

**configs/models.json**
```json
{ "hidden_size": 128, "num_layers": 2, "fc_hidden": 256 }
```

---

## 8. Implementation Phases

### Phase 1 — Infrastructure & Config
- Create `configs/*.json` (4 files)
- Create `.gitignore`, `outputs/.gitkeep`
- Install all dependencies via `uv add`

### Phase 2 — Data Service
- Fix `src/services/data_generator.py`: add S5 (sum signal), one-hot size 5
- Add windowing + normalization to [-1, 1]
- Unit tests: `tests/unit/test_signals.py`

### Phase 3 — SDK Models
- Add `src/sdk/models/base.py` (abstract BaseModel)
- Fix `mlp.py`, `rnn.py`, `lstm.py`: output W samples (not 1)
- Unit tests: `tests/unit/test_models.py`

### Phase 4 — Training Pipeline
- Fix `src/services/train.py`: target shape (W,), MSE loss, Adam
- Add `tests/unit/test_trainer.py`

### Phase 5 — Experiments & Results
- Build `src/services/experiment_runner.py` (135-run loop)
- Build `src/services/results_collector.py` (results.json output)
- Integration tests: `tests/integration/test_experiments.py`

### Phase 6 — Reporting
- Fix `src/services/research_visualizer.py`: reconstruction plots, loss curves
- Comparison table (45 rows × 3 model columns)
- All plots saved as PNG via `plt.savefig()` — no `plt.show()`

### Phase 7 — SDK + Integration
- Build `src/sdk/hw1_sdk.py` (wraps all services)
- `tests/conftest.py` + `tests/integration/test_sdk.py`
- `uv run pytest --cov=src --cov-fail-under=85`

### Phase 8 — Docs & README
- Finalize `docs/TODO.md`
- Expand `README.md` with graphs, comparison table, analysis

---

## 9. Quality Assurance
- **Unit Tests:** SDK components (models, data, training)
- **Integration Tests:** full Signal Gen → Train → Eval → Results pipeline
- **Linting:** `uv run ruff check src/` — zero errors
- **Coverage:** `uv run pytest --cov=src --cov-fail-under=85` — ≥ 85%
- **File size:** all source files strictly under 150 lines
