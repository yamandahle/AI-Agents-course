# PRD — HW1: RNN/LSTM Sine Wave Source Separation

## 1. Project Overview

### Problem Statement
Given a noisy observation of the **mixture signal S5** (sum of all 4 sine waves) plus a one-hot vector indicating **which** individual signal to extract, reconstruct the clean window of that individual signal. This is a **source separation** task: the model must learn to isolate one frequency component from a noisy mixture.

### Target Audience
AI Agents course submission — demonstrating the ability to build, train, and evaluate sequence models (FC, RNN, LSTM) on a signal source separation task.

### Goals
- Implement a full data pipeline: signal generation → noisy S5 mixture dataset → windowed samples
- Train and compare 3 model architectures: Fully Connected, RNN, LSTM
- Run systematic experiments across signal type, noise level, and window size
- Produce a visual and quantitative analysis of model performance

---

## 2. Signal Definitions

### Base Formula
```
y(t) = A * sin(2π * f * t + φ)
```
Where `φ ~ Uniform(0, 2π)` is a random phase assigned once per signal.

### Noisy Formula
```
y_noisy(t) = (A + alpha * σ) * sin(2π * f * t + φ + beta * σ)
```
Where `σ ~ N(0, 1)` is re-sampled fresh for every generated window.

### The Signals

| Signal | Frequency (Hz) | Amplitude | Phase            | Role in Task      |
|--------|---------------|-----------|------------------|-------------------|
| S1     | 1             | 1.0       | φ ~ U(0, 2π)    | Extraction target |
| S2     | 2             | 1.0       | φ ~ U(0, 2π)    | Extraction target |
| S3     | 5             | 1.0       | φ ~ U(0, 2π)    | Extraction target |
| S4     | 10            | 1.0       | φ ~ U(0, 2π)    | Extraction target |
| S5     | —             | —         | —                | **Noisy input** (S1+S2+S3+S4 sum) |

### Sampling Parameters
- Duration: 10 seconds per signal
- Sampling rate: 1000 Hz
- Total samples per signal: 10,000

---

## 3. Dataset Requirements

### Windowing
- Sliding window of size W (default W=10 samples, as defined in lecture)
- Stride = 1 (overlapping windows)

### Sample Structure
```
input  = [one_hot_vector (4,)] + [noisy_S5_window (W,)]  → shape: (W+4,)  e.g. (14,)
target = clean_Si_window (W,)                             → shape: (W,)    e.g. (10,)
```
The **input is always a window of the noisy mixture S5**. The one-hot vector tells the model which individual signal to extract from it.

### One-Hot Encoding
- Size **4** vector, one entry per extractable signal (S1–S4)
- Example: extract S2 → [0, 1, 0, 0]

### Dataset Split
- 80% training, 20% testing
- All 4 extraction targets represented in both splits
- Seed: 42

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

### Dimensions to Vary

| Dimension    | Values                        |
|-------------|-------------------------------|
| Signal       | S1, S2, S3, S4                |
| Noise level  | low (α=0.05, β=0.05), med (α=0.1, β=0.1), high (α=0.3, β=0.3) |
| Window size  | W=5, W=10, W=20               |
| Model        | FC, RNN, LSTM                 |

### Total Runs
4 × 3 × 3 × 3 = **108 training runs**

### Per-Run Recording
- Train loss history (per epoch)
- Validation loss history (per epoch)
- Best validation MSE + best epoch

---

## 6. Success Criteria (KPIs)

### Quality Gates
| Criterion | Requirement |
|-----------|-------------|
| All models train | No NaN loss on any signal/noise/window combo |
| Results file | `outputs/results/results.json` with 108 entries |
| Figures | At least 1 reconstruction plot per model (noisy S5 input vs clean target vs predicted) |
| Loss curves | Per model, showing convergence over 50 epochs |
| Comparison table | 36 rows (signal × noise × window), 3 model columns |
| Test coverage | ≥ 85% via pytest-cov |
| Linting | 0 Ruff errors |

### MSE Targets (best-case, low noise, W=10)
| Model | Target MSE |
|-------|-----------|
| FC    | < 0.05    |
| RNN   | < 0.02    |
| LSTM  | < 0.01    |

---

## 7. Non-Functional Requirements

- All config values in `config/setup.json` — nothing hardcoded in source
- Max 150 lines per source file
- SDK architecture: all business logic through `HW1SDK`
- OOP design — no code duplication
- `uv` as sole package manager
- No secrets in source code
- All plots saved as PNG via `plt.savefig()` — no `plt.show()`
- Signals normalized to [-1, 1] before training

---

## 8. Out of Scope
- Real-time signal processing
- Deployment / serving
- GPU-specific optimization (code auto-detects CUDA if available)
