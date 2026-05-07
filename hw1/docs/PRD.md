# PRD — HW1: RNN/LSTM Sine Wave Source Separation

## 1. Project Overview

### Problem Statement
Given a noisy observation of the **mixture signal S5** (sum of all 4 sine waves) plus a one-hot vector indicating **which** individual signal to extract, reconstruct the clean window of that individual signal. This is a **source separation** task: the model must learn to isolate one frequency component from a noisy mixture.

### Target Audience
AI Agents course submission — demonstrating the ability to build, train, and evaluate sequence models (FC, RNN, LSTM) on a signal source separation task.

### Goals
- Implement a full data pipeline: signal generation → noisy S5 mixture dataset → windowed samples
- Train and compare 3 model architectures: Fully Connected, RNN, LSTM
- Run systematic experiments across signal type and noise level at the lecture-specified window size
- Produce a visual and quantitative analysis of model performance

---

## 2. Signal Definitions

### Base Formula
```
y(t) = A * sin(2π * f * t + φ)
```

### Noisy Formula
```
y_noisy(t) = (A + alpha * σ) * sin(2π * f * t + φ + beta * σ)
```
Where `σ ~ N(0, 1)` is re-sampled fresh for every generated window.

### The Signals

| Signal | Frequency (Hz) | Amplitude | Role in Task      |
|--------|---------------|-----------|-------------------|
| S1     | 1             | 1.0       | Extraction target |
| S2     | 2             | 1.0       | Extraction target |
| S3     | 5             | 1.0       | Extraction target |
| S4     | 10            | 1.0       | Extraction target |
| S5     | —             | —         | **Noisy input** (S1+S2+S3+S4 sum) |

### Sampling Parameters
- Duration: 10 seconds per signal
- Sampling rate: 1000 Hz
- Total samples per signal: 10,000

---

## 3. Dataset Requirements

### Windowing
- Sliding window of size **W = 10 samples** (fixed per lecture requirement)
- Stride = 1 (overlapping windows)
- Vectorised using `numpy.lib.stride_tricks.sliding_window_view` (build time ~0.06 s)

### Sample Structure
```
input  = [one_hot_vector (4,)] + [noisy_S5_window (W,)]  → shape: (W+4,)  e.g. (14,)
target = clean_Si_window (W,)                             → shape: (W,)    e.g. (10,)
```
The **input is always a window of the noisy mixture S5**. The one-hot vector (size 4, one entry per signal S1–S4) tells the model which individual signal to extract.

### Dataset Split
- 80% training, 20% validation
- All 4 extraction targets represented in both splits
- Seed: 42
- Total: 4 signals × 9,990 windows = **39,960 samples**

### Normalization
- Each clean individual signal (Si) normalized to [-1, 1] before windowing
- Clean S5 normalized by its own max amplitude for the noisy input

---

## 4. Model Specifications

### Model 1 — Fully Connected (FC)
```
Input:  (W+4,)  e.g. (14,) when W=10
Linear(W+4, 256) → ReLU
Linear(256, 256)  → ReLU
Linear(256, W)
Output: (W,)  e.g. (10,)
```

### Model 2 — RNN
```
Input: noisy_S5_window (W, 1) + one_hot as initial hidden state
one_hot → Linear(4, 128) → h0 of shape (num_layers, batch, 128)
RNN(input_size=1, hidden_size=128, num_layers=2, batch_first=True)
last hidden state → Linear(128, W)
Output: (W,)  e.g. (10,)
```

### Model 3 — LSTM
```
Same as RNN but with cell state:
one_hot → Linear(4, 128) → h0 and c0
LSTM(input_size=1, hidden_size=128, num_layers=2, batch_first=True)
last output step → Linear(128, W)
Output: (W,)  e.g. (10,)
```

### Training Configuration
| Parameter    | Value  |
|-------------|--------|
| Loss        | MSE    |
| Optimizer   | Adam   |
| LR          | 0.001  |
| Epochs      | 50     |
| Batch size  | 64     |
| Seed        | 42     |

---

## 5. Experiments

### Dimensions

| Dimension    | Values                                         |
|-------------|------------------------------------------------|
| Signal       | S1, S2, S3, S4                                 |
| Noise level  | low (α=0.05, β=0.05), high (α=0.30, β=0.30)   |
| Window size  | W=10 (fixed per lecture)                       |
| Model        | FC, RNN, LSTM                                  |

### Total Runs
4 signals × 2 noise levels × 3 models = **6 training runs**
Each run evaluated on all 4 signals → **24 result entries**

### Per-Run Recording
- Train loss history (per epoch)
- Validation loss history (per epoch)
- Per-signal best validation MSE (evaluated on 200 held-out windows)
- Best epoch (minimum mixed-signal val loss)

---

## 6. Success Criteria (KPIs)

### Quality Gates
| Criterion | Requirement |
|-----------|-------------|
| All models train | No NaN loss on any signal/noise combo |
| Results file | `outputs/results/results.json` with 24 entries |
| Figures | 4 figure types × 4 signals = 16 plots + 1 signals overview = 17 PNGs |
| Loss curves | Per model, showing convergence over 50 epochs |
| Comparison table | Printed to console: signal × noise × model |
| Test suite | 37 unit tests passing |
| Linting | 0 Ruff errors |

### Achieved MSE Results (best val MSE, low noise, W=10)

| Signal | FC     | RNN    | LSTM   |
|--------|--------|--------|--------|
| S1 (1Hz)  | 0.0782 | 0.1534 | 0.0924 |
| S2 (2Hz)  | 0.1199 | 0.1300 | 0.0699 |
| S3 (5Hz)  | 0.1442 | 0.1888 | 0.1235 |
| S4 (10Hz) | 0.0099 | 0.0787 | 0.0155 |

S4 (10Hz) is significantly easier because its frequency is most distinguishable within a 10ms window.

---

## 7. Non-Functional Requirements

- All config values in `config/setup.json` — nothing hardcoded in source modules
- Source modules strictly under 150 lines each (entry-point scripts `run_all.py` / `run_test.py` are exempt as orchestrators)
- SDK architecture: models in `src/sdk/models/`, services in `src/services/`
- OOP design — `BaseModel` abstract class with `save`/`load` interface
- `uv` as sole package manager
- No secrets in source code (`.env-example` provided)
- All plots saved as PNG via `plt.savefig()` — no `plt.show()`
- Signals normalized to [-1, 1] before training

---

## 8. Out of Scope
- Real-time signal processing
- Deployment / serving
- GPU-specific optimization (code auto-detects CUDA if available)
- Medium noise level (α=β=0.10) — excluded per experiment design decision
