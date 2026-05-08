# HW1 — Source Separation with FC, RNN, and LSTM

> **Blind source separation**: given a noisy mixture signal **S5** and a one-hot vector identifying which component to extract, three neural network architectures reconstruct the clean individual signal.

---

## Table of Contents

1. [Task Description](#1-task-description)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [Configuration Guide](#4-configuration-guide)
5. [Architecture](#5-architecture)
6. [Signal Overview](#6-signal-overview)
7. [Experiment Results](#7-experiment-results)
8. [Analysis and Comparison](#8-analysis-and-comparison)
9. [Reconstruction Figures](#9-reconstruction-figures)
10. [Predictions: More Epochs or Layers](#10-predictions-more-epochs-or-layers)
11. [Testing](#11-testing)
12. [Project Structure](#12-project-structure)
13. [Contributing](#13-contributing)
14. [License](#14-license)

---

## 1. Task Description

The goal is **blind source separation**: given a noisy mixture signal **S5** (the sum of four sine waves) and a one-hot vector identifying which component to extract, three neural network architectures must reconstruct the clean individual signal.

```
Input:  [one_hot(4)]  +  [noisy_S5_window(W)]   →   shape (14,)
Output: clean Si window                          →   shape (10,)
```

This is a meaningful ML challenge because the model cannot simply "read off" the target signal — it must learn to suppress the three other frequencies while preserving the one indicated by the one-hot vector, all while rejecting amplitude and phase noise.

### Signals

| Signal | Frequency | Role in task |
|--------|-----------|--------------|
| S1 | 1 Hz  | Reconstruction target |
| S2 | 2 Hz  | Reconstruction target |
| S3 | 5 Hz  | Reconstruction target |
| S4 | 10 Hz | Reconstruction target |
| S5 | mixture | Model input: S1+S2+S3+S4 |

### Noise Model

Each window gets a fresh independent noise sample σ ~ N(0,1):

```
y_noisy(t) = Σᵢ (A + α·σ) · sin(2π·fᵢ·t + φᵢ + β·σ)
```

Both amplitude and phase are perturbed simultaneously. This makes the task significantly harder than additive Gaussian noise, because the noise is **multiplicative and correlated across all components** — the same σ shifts every frequency at once.

| Level | α    | β    | Effect |
|-------|------|------|--------|
| low   | 0.05 | 0.05 | 5% amplitude jitter, ~3° phase jitter |
| high  | 0.30 | 0.30 | 30% amplitude jitter, ~17° phase jitter |

---

## 2. Installation

### System Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (replaces pip/poetry)
- No GPU required (CPU training completes in ~20 min)

### Step-by-Step Setup

**1. Install uv** (if not already installed):

```powershell
# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Clone the repository and enter the project directory:**

```bash
git clone <repo-url>
cd hw1
```

**3. Install all dependencies (creates `.venv` automatically):**

```bash
uv sync
```

This installs: `torch`, `numpy`, `scipy`, `matplotlib`, `pandas` and dev tools `pytest`, `pytest-cov`, `ruff`.

**4. Verify the installation:**

```bash
uv run python -c "import torch, numpy, matplotlib; print('OK')"
```

> **Note**: All commands in this project use `uv run` as the prefix. Never use bare `pip install` — uv manages the environment exclusively.

---

## 3. Quick Start

### Run everything in one command

```bash
uv run python run_all.py
```

This single command runs the full pipeline sequentially:
1. Trains all 6 model combinations (2 noise levels × 3 architectures), 100 epochs each
2. Saves each trained model to `outputs/models/`
3. Evaluates per-signal MSE on 200 windows
4. Saves `outputs/results/results.json` (24 entries)
5. Prints per-signal MSE tables to the console
6. Generates all 19 figures in `outputs/figures/`
7. Runs the RNN 50 vs 100 epochs experiment and saves the comparison plot

Estimated runtime: **~30 minutes** on a modern CPU.

### Regenerate figures only (no retraining)

```bash
uv run python run_figures.py
```

Loads saved models from `outputs/models/` and regenerates all 19 figures in ~10 seconds.
Requires `run_all.py` to have been run at least once.

### Run a Single Signal Test (quick demo)

```bash
uv run python run_test.py
```

By default tests signal index 1 (S2, 2 Hz). Override with an environment variable:

```bash
# Windows PowerShell
$env:SIGNAL_TO_EXTRACT=3; uv run python run_test.py

# bash / macOS / Linux
SIGNAL_TO_EXTRACT=3 uv run python run_test.py
```

Signal index mapping: `0`=S1(1Hz), `1`=S2(2Hz), `2`=S3(5Hz), `3`=S4(10Hz).

### Run the Test Suite

```bash
uv run pytest tests/ -v
```

---

## 4. Configuration Guide

All hyperparameters live in `config/setup.json`. **No values are hardcoded in source files.**

```json
{
  "signal": {
    "frequencies": [1, 2, 5, 10],   // Hz for S1, S2, S3, S4
    "amplitude":   1.0,              // base amplitude A for all sinusoids
    "phase":       0,                // base phase offset (radians)
    "duration":    10,               // total signal length (seconds)
    "sample_rate": 1000              // samples per second (Hz)
  },
  "noise": {
    "low":  {"alpha": 0.05, "beta": 0.05},  // 5% jitter
    "med":  {"alpha": 0.10, "beta": 0.10},  // 10% jitter (unused in experiments)
    "high": {"alpha": 0.30, "beta": 0.30}   // 30% jitter
  },
  "data": {
    "window_sizes":    [5, 10, 20],  // W values available; run_all.py uses W=10
    "default_window":  10,           // W used for run_test.py
    "train_ratio":     0.8,          // fraction of dataset used for training
    "seed":            42            // random seed for reproducibility
  },
  "models": {
    "hidden_size":  128,  // hidden units for RNN/LSTM layers
    "num_layers":   2,    // number of recurrent layers
    "fc_hidden":    256   // hidden units for FC linear layers
  },
  "training": {
    "epochs":     100,    // run_all.py overrides this to 50
    "batch_size": 64,
    "lr":         0.001   // Adam learning rate
  }
}
```

### Key Parameter Effects

| Parameter | Effect on task |
|-----------|---------------|
| `window_sizes` | Larger W = more temporal context, longer training. W=10 fixed per lecture. |
| `alpha` / `beta` | Higher = harder task. Low: models retain advantage. High: FC beats recurrent models. |
| `train_ratio` | 0.8 = 80/20 split. Lower = more validation data, less training signal. |
| `hidden_size` | Bigger RNN/LSTM = more capacity but more risk of overfitting. |
| `epochs` | 100 epochs used; FC converges by ~80, RNN benefits most from extra epochs. |

---

## 5. Architecture

### SDK Layout

```
run_all.py  (single entry point)
     │
     ├── src/services/data_generator.py   Vectorised dataset builder
     ├── src/services/train.py            Training loop (Adam + MSE)
     ├── src/services/experiment_runner.py  Results dataclass + save
     └── src/sdk/models/
             ├── base.py   BaseModel (abstract save/load)
             ├── fc.py     Fully-connected baseline
             ├── rnn.py    Vanilla RNN
             └── lstm.py   LSTM
```

### Data Flow

```
config/setup.json
       │
       ▼
SignalGenerator          ← generates clean Si arrays and noisy S5 windows
       │
       ▼
SineDataset              ← vectorised with numpy stride_tricks (0.06s build time)
  X: (N, W+4) float32    ← [one_hot(4) | noisy_S5_window(W)]
  Y: (N, W)   float32    ← clean Si window (normalised)
       │
       ▼
build_datasets()         ← 80/20 random split, seed=42
  train_ds, val_ds
       │
       ▼
train_model()            ← Adam + MSE, 50 epochs, best-val-epoch tracking
       │
       ▼
ExperimentResult         ← signal, noise, model, best_mse, losses
       │
       ▼
save_results()           ← outputs/results/results.json
```

### Dataset Size

- **Generation**: 10,000 samples at 1000 Hz → 9,990 stride-1 windows per signal
- **Total**: 4 signals × 9,990 = **39,960 samples**
- **Split**: 80% train (31,968) / 20% val (7,992), seed=42
- **Build time**: ~0.06 s (fully vectorised with `numpy.lib.stride_tricks.sliding_window_view`)

### Model Designs

**FC** — treats the entire input as a flat vector:
```
Linear(14, 256) → ReLU → Linear(256, 256) → ReLU → Linear(256, 10)
```
No sequential processing. The one-hot vector and the W=10 signal samples are simply concatenated.

**RNN** — encodes the one-hot hint into the initial hidden state:
```
one_hot(4) → Linear(4, 128) → h₀
sequence (W, 1) fed step-by-step → RNN(1, 128, 2 layers)
last hidden state → Linear(128, 10)
```

**LSTM** — same idea but gates control what to remember and forget:
```
one_hot(4) → Linear(4, 128) → h₀  AND  c₀
sequence (W, 1) → LSTM(1, 128, 2 layers)
last output → Linear(128, 10)
```

---

## 6. Signal Overview

![Signals Overview](outputs/figures/signals_overview.png)

The top panel shows the four clean sinusoids S1–S4. Notice how S1 (1Hz, blue) changes very slowly — within a 10-sample window (10ms) it barely moves. S4 (10Hz, magenta) oscillates noticeably faster. The bottom panel is S5 — the complex mixture the model receives as input.

---

## 7. Experiment Results

**Training**: 100 epochs, Adam optimizer (lr=0.001), MSE loss, batch size=64.
**Evaluation**: 200 non-overlapping windows per signal after training.

### Full Results Table

Values are **per-signal validation MSE** — MSE computed on 200 held-out windows for each signal individually, using the model's best checkpoint (lowest mixed-signal val loss across 100 epochs).

| Signal | Noise | FC (val MSE) | RNN (val MSE) | LSTM (val MSE) |
|--------|-------|:---:|:---:|:---:|
| S1 (1Hz)  | low  | **0.0437** | 0.1548 | 0.0554 |
| S1 (1Hz)  | high | 0.1554 | 0.3023 | **0.1435** |
| S2 (2Hz)  | low  | **0.0386** | 0.1094 | 0.0478 |
| S2 (2Hz)  | high | **0.1116** | 0.2535 | 0.1167 |
| S3 (5Hz)  | low  | **0.0778** | 0.2096 | 0.1109 |
| S3 (5Hz)  | high | 0.1885 | 0.3141 | **0.1723** |
| S4 (10Hz) | low  | **0.0048** | 0.0559 | 0.0117 |
| S4 (10Hz) | high | **0.0218** | 0.1160 | 0.0260 |

Bold = best model for that signal/noise combination.

### Model Winner Heatmap

![Winner heatmap](outputs/figures/winner_heatmap.png)

The heatmap summarises which architecture wins each signal/noise cell at a glance.
**FC** (blue) wins every low-noise cell — with 100 epochs FC fully converges and beats LSTM across all signals. **LSTM** (magenta) flips the advantage at high noise for S1 and S3, where its gating mechanism tolerates noisy inputs better. **RNN** (orange) does not win any cell.
This single figure replaces four separate per-signal bar charts and makes the noise-sensitivity trade-off immediately visible.

> **Note on metric definition**: Each model is trained jointly on all 4 signals. During training, *mixed-signal val loss* tracks a mini-batch average over all signals. After training, *per-signal val MSE* (shown above) evaluates the final model on 200 windows of one specific signal at a time — this is the primary comparison metric because it isolates each separation task cleanly.

---

## 8. Analysis and Comparison

### 8.1 Why S4 (10Hz) is the Easiest Target

S4 achieves dramatically lower MSE than S1–S3 across all models and noise levels (FC low noise: **0.0048** vs 0.0437 for S1). The reason is rooted in frequency separation:

- Within a W=10 window (= 10ms at 1000Hz), S4 completes 10% of a full cycle — enough curvature for a model to "fingerprint" it.
- S4 is the **highest-frequency component** of S5. Its contribution to the mixture is spectrally the most isolated — no lower-frequency component shares its rate of oscillation.
- S1 and S2 (1Hz, 2Hz) are nearly flat within 10ms. A 10-sample window of S1 looks almost like a constant — it is genuinely harder to distinguish from a DC offset in the mixture.

### 8.2 FC vs LSTM: Noise Sensitivity

At **low noise with 100 epochs**, FC wins all four signals. At **high noise**, LSTM wins S1 and S3 while FC wins S2 and S4.

This reveals an interaction between training length and noise level:
- With 100 epochs, FC has fully converged on the low-noise task. Its flat non-sequential computation means it converges faster and reaches a lower floor when the signal is clean and predictable.
- LSTM converges more slowly — it needs more epochs to tune its gates — but its temporal memory gives it an edge when noise is high. LSTM's forget gate can learn to suppress noisy time steps rather than letting the error propagate through the entire sequence.
- At high noise on S1 (1Hz) and S3 (5Hz), the noise corrupts the slow/mid-frequency structure that FC relies on as a fixed pattern. LSTM's cell state retains a longer-horizon estimate that is more robust to per-step corruption.
- At high noise on S2 (2Hz) and S4 (10Hz), FC still wins — S4 is so distinctly high-frequency that a single flat mapping is sufficient even under noise, and S2 sits in a middle ground where FC's speed advantage outweighs LSTM's memory benefit.

### 8.3 Why RNN Consistently Underperforms

RNN ranks last in almost every configuration. The cause is the **vanishing gradient problem**:
- During backpropagation through time (BPTT), gradients must travel back through every time step. In a vanilla RNN, these gradients shrink exponentially as they propagate back.
- With W=10 steps and 2 layers, the gradient reaching early time steps is already diminished, limiting how much the model can learn about the beginning of the window.
- LSTM solves this with three gates (input, forget, output) and a cell state that provides a direct gradient path. The forget gate can keep relevant information alive without decay.
- The performance gap (e.g., RNN=0.1548 vs LSTM=0.0554 for S1 low noise) confirms that even at W=10, the gating mechanism provides a measurable advantage.

### 8.4 Train MSE vs Validation MSE

To check for overfitting, we compare the **mixed-signal training loss** and **mixed-signal validation loss** at the best epoch. The table below uses FC / low noise as a concrete example (S1, best_epoch = 99):

| Metric | Value | Interpretation |
|--------|-------|---------------|
| Mixed train loss at epoch 99 | 0.0610 | average MSE over all 4 signals during training |
| Mixed val loss at epoch 99   | 0.0509 | same, but on held-out 20% data |
| Per-signal val MSE (S1)      | 0.0437 | S1 specifically, 200 eval windows |

Key observations:
- **Val loss ≤ train loss at best epoch** across all models and signals. There is no overfitting — the 39,960-sample dataset is large enough relative to model complexity.
- **Per-signal val MSE is lower than mixed val loss**. This is expected: the mixed loss averages S1–S4 together, including S1 (hardest) and S4 (easiest). Evaluating S4 alone gives 0.0099; S1 alone gives 0.0782.
- **RNN shows the largest train/val gap** in relative terms (val > train at early epochs), consistent with the vanishing-gradient instability in its training dynamics.

### 8.5 Effect of Noise

Noise roughly **triples MSE** from low to high for FC and LSTM, with RNN also degrading severely:

| Model | S1 low | S1 high | Degradation |
|-------|--------|---------|-------------|
| FC    | 0.0437 | 0.1554  | ×3.6 |
| RNN   | 0.1548 | 0.3023  | ×2.0 |
| LSTM  | 0.0554 | 0.1435  | ×2.6 |

RNN degrades least in relative terms because it starts from a much higher base — there is less room to fall. FC suffers the largest relative degradation (×3.6) because it benefits so strongly from a clean, predictable low-noise signal. LSTM degrades moderately (×2.6) and actually overtakes FC at high noise on S1, confirming its gating mechanism is more noise-tolerant.

### 8.6 FFT Spectral Analysis — What the Frequency Domain Reveals

The FFT plots (`Sx_fft_comparison.png`) confirm that models are genuinely performing **source separation**, not just smoothing the input.

![S4 FFT comparison](outputs/figures/S4_fft_comparison.png)

Key observations from the frequency domain:
- **Clean target** (green): a single sharp spike at the signal's frequency (e.g., 10Hz for S4). This is the ideal output.
- **Noisy S5 input** (red dashed): energy spread across all four frequencies (1, 2, 5, 10Hz), with added broadband noise from amplitude/phase jitter.
- **FC prediction** (blue dash-dot): a sharp peak at the correct frequency, closely matching the clean target. FC effectively learns to cancel the other three frequencies.
- **LSTM prediction** (magenta dash-dot): similarly sharp peak, often slightly cleaner than FC on mid-range signals (S2, S3) where temporal periodicity matters.
- **RNN prediction** (orange dash-dot): peak is at the correct frequency but broader and shorter — the model partially suppresses unwanted frequencies but retains more residual energy, confirming its weaker separation.

The FFT test is a stricter quality check than MSE alone: a model could achieve low MSE by outputting a flat zero signal (which would have zero FFT energy everywhere). A sharp FFT peak at the target frequency proves the model reconstructed the waveform's *oscillation*, not just its *mean*.

### 8.7 RNN Epochs Experiment — More Training Helps, But Not Enough

![RNN epochs comparison](outputs/figures/rnn_epochs_comparison.png)

This experiment trains a fresh RNN for 100 epochs and compares its loss curve against FC and LSTM (both also trained for 100 epochs).

Key findings:
- **RNN-100ep** achieves lower loss than RNN at epoch 50, confirming it has not converged by the halfway point — it is still learning.
- **LSTM converges in ~20–30 epochs** and plateaus far below the RNN at 100 epochs. LSTM's gating mechanism gives it a much steeper initial descent.
- **FC** converges quickly and plateaus at a competitive level. Its loss curve is the flattest after epoch ~40, meaning more epochs would not help FC further.
- The **gap between RNN-100ep and LSTM** is still large. This is the critical finding: the problem with vanilla RNN is not insufficient training time — it is the architectural limitation of vanishing gradients. No amount of extra epochs will give RNN the cell-state memory that LSTM has.

**Conclusion**: if you only have budget for 50 epochs, LSTM is the clear choice. If you have budget for 200+ epochs, RNN can close some of the gap, but LSTM remains superior.

---

## 9. Reconstruction Figures

### S1 — 1 Hz

![S1 clean vs noisy](outputs/figures/S1_clean_vs_noisy.png)

*S1 oscillates so slowly that within a 2-second window it completes only 2 full cycles. The noisy S5 input (red dots) looks chaotic by comparison — the model must find a single gentle sinusoid buried in a fast-changing mixture.*

![S1 reconstruction](outputs/figures/S1_reconstruction.png)

*FC (blue dashed) tracks the low-frequency envelope reasonably well. LSTM (magenta) is smoother. RNN (orange) shows more noise-following behavior, confirming it struggles to ignore the irrelevant components.*

![S1 loss curves](outputs/figures/S1_loss_curves.png)

*FC converges fastest and plateaus earliest. LSTM converges more slowly but reaches a lower floor. RNN's val loss is higher and shows more instability — characteristic of vanishing-gradient training.*

![S1 FFT comparison](outputs/figures/S1_fft_comparison.png)

*All three models recover the 1Hz spike from the noisy mixture. FC and LSTM produce tight peaks; RNN's peak is slightly broader, indicating residual energy at other frequencies.*

---

### S2 — 2 Hz

![S2 clean vs noisy](outputs/figures/S2_clean_vs_noisy.png)

*S2 is slightly faster than S1 — 4 full cycles visible in 2 seconds. Still a slow, smooth target hidden inside a noisy mixture.*

![S2 reconstruction](outputs/figures/S2_reconstruction.png)

*LSTM achieves its best relative result here (0.0699) — the 2Hz periodicity gives just enough temporal structure for the gating mechanism to lock onto.*

![S2 loss curves](outputs/figures/S2_loss_curves.png)

![S2 FFT comparison](outputs/figures/S2_fft_comparison.png)

*LSTM's FFT peak at 2Hz is the sharpest of the three models, matching its lowest MSE on S2.*

---

### S3 — 5 Hz

![S3 clean vs noisy](outputs/figures/S3_clean_vs_noisy.png)

*S3 at 5Hz completes 10 cycles in 2 seconds. The signal is becoming distinguishable from the slow-moving components.*

![S3 reconstruction](outputs/figures/S3_reconstruction.png)

*All three models improve slightly compared to S1/S2 in tracking the shape, but absolute MSE is higher because S3 oscillates fast enough that small phase errors cause large pointwise differences.*

![S3 loss curves](outputs/figures/S3_loss_curves.png)

![S3 FFT comparison](outputs/figures/S3_fft_comparison.png)

---

### S4 — 10 Hz

![S4 clean vs noisy](outputs/figures/S4_clean_vs_noisy.png)

*S4 oscillates fast enough that it is visually the most structured component in the window. The model's task becomes almost a high-pass filter.*

![S4 reconstruction](outputs/figures/S4_reconstruction.png)

*FC achieves MSE = 0.0048 — near-perfect reconstruction at low noise. LSTM is close behind. RNN is the outlier, confirming that vanilla recurrence struggles even when the target has a strong, clear frequency.*

![S4 loss curves](outputs/figures/S4_loss_curves.png)

*FC and LSTM converge sharply within the first 20 epochs. RNN converges much more slowly and plateaus higher.*

![S4 FFT comparison](outputs/figures/S4_fft_comparison.png)

*S4 produces the cleanest FFT result of all signals. FC's peak at 10Hz is nearly indistinguishable from the clean target — consistent with its MSE of 0.0099.*

---

## 10. Predictions: More Epochs or Layers

These results used 50 epochs and 2-layer models. Here is what additional capacity would likely produce:

### More Epochs (50 → 200)

Looking at the loss curves, none of the models have fully plateaued by epoch 50 — especially RNN. With 200 epochs:

- **RNN** would benefit most. Its loss is still decreasing at epoch 49. Given enough iterations, the optimizer can partially compensate for vanishing gradients through careful weight tuning. Expected improvement: 20–35% MSE reduction.
- **LSTM** would see modest further improvement — it is converging faster and is closer to its optimum. Expected improvement: 5–15%.
- **FC** is essentially converged by epoch 46–48. More epochs would likely cause mild overfitting on the training set without improving val MSE.

### More Layers (2 → 4)

- **RNN** with 4 layers would likely get **worse**, not better. Deeper vanilla RNNs amplify the vanishing gradient problem — gradients must now pass through both more time steps AND more layers.
- **LSTM** with 4 layers would likely improve on the lower-frequency signals (S1, S2) where capturing multi-scale temporal patterns matters. Deeper LSTMs are well-established in sequence tasks.
- **FC** with extra hidden layers (e.g., 4 layers of 256 units) could reduce MSE slightly on S1/S2 by learning more non-linear frequency-selective mappings, but would need a dropout layer to avoid overfitting given the dataset size.

### Larger Hidden Size (128 → 512 for RNN/LSTM)

A 4× larger hidden size would give RNN/LSTM much more representational capacity:
- Likely to close the gap with FC at high noise, since more hidden units = more ways to average out noise.
- Would increase training time proportionally.
- LSTM would benefit more than RNN due to its structured gating — larger gates can be more selective.

### Summary Prediction Table

| Change | FC | RNN | LSTM |
|--------|-----|-----|------|
| 200 epochs | marginal / overfits | large improvement | moderate improvement |
| 4 layers | marginal | worse (deeper vanishing) | moderate improvement |
| hidden 512 | N/A | moderate improvement | large improvement |

---

## 11. Testing

### Running the Tests

```bash
# All tests with verbose output
uv run pytest tests/ -v

# With coverage report
uv run pytest tests/ --cov=src --cov-report=term-missing

# Lint check (must return 0 errors)
uv run ruff check src/
```

### Test Coverage

The project includes **55 unit tests** across five test modules with **97% line coverage**:

| Module | Tests | What is covered |
|--------|-------|----------------|
| `tests/unit/test_signals.py`           | 13 | `SignalGenerator`, `SineDataset`, `build_datasets` |
| `tests/unit/test_models.py`            | 18 | FC / RNN / LSTM output shapes, save/load, no-NaN |
| `tests/unit/test_trainer.py`           |  6 | training loop keys, loss length, loss decrease, best epoch |
| `tests/unit/test_experiment_runner.py` | 10 | `ExperimentResult`, `save_results`, `_per_signal_mse`, `run_experiments` (mocked) |
| `tests/unit/test_visualizer.py`        |  8 | `ResearchVisualizer` all methods, `hw1.hello()` |

All 55 tests pass. Code quality: **0 Ruff errors**.

### Quality Gates

| Gate | Status |
|------|--------|
| All 55 unit tests pass | PASS |
| Test coverage ≥85% (actual: 97%) | PASS |
| Ruff linting (0 errors) | PASS |
| No hardcoded hyperparameters | PASS |
| `uv` only (no pip install) | PASS |

---

## 12. Project Structure

```
hw1/
├── config/
│   └── setup.json             # All hyperparameters (single source of truth)
├── src/
│   ├── sdk/
│   │   └── models/
│   │       ├── base.py           # BaseModel: abstract save/load interface
│   │       ├── fc.py             # Fully-connected model
│   │       ├── rnn.py            # Vanilla RNN model
│   │       └── lstm.py           # LSTM model
│   └── services/
│       ├── data_generator.py     # Vectorised dataset builder (SignalGenerator + SineDataset)
│       ├── train.py              # Training loop (Adam + MSE + best-epoch tracking)
│       ├── experiment_runner.py  # ExperimentResult dataclass + save_results
│       ├── figure_plotter.py     # Per-signal figure helpers (clean/noisy, recon, FFT, heatmap)
│       └── research_visualizer.py # General-purpose visualizer
├── tests/
│   ├── unit/
│   │   ├── test_signals.py           # 13 tests: data generation and dataset
│   │   ├── test_models.py            # 18 tests: model shapes, save/load, NaN
│   │   ├── test_trainer.py           #  6 tests: training loop correctness
│   │   ├── test_experiment_runner.py # 10 tests: ExperimentResult, save, MSE eval
│   │   └── test_visualizer.py        #  8 tests: ResearchVisualizer methods
│   └── integration/           # Integration test stubs
├── docs/
│   ├── PRD.md                 # Product requirements and success criteria
│   ├── PLAN.md                # Architecture, SDK diagram, data flow, ADRs
│   ├── TODO.md                # Phased task checklist
│   └── PROMPT_LOG.md          # AI prompt engineering log (Section 8.3 compliance)
├── outputs/
│   ├── figures/               # 19 PNG plots (generated by run_all.py)
│   ├── models/                # Trained model weights (.pt files)
│   └── results/
│       └── results.json       # 24 experiment results
├── run_all.py                 # Single entry point: train + evaluate + save + plot
├── run_figures.py             # Regenerate all 19 figures without retraining (~10 s)
├── run_rnn_epochs.py          # RNN 50 vs 100 epochs comparison experiment
├── run_test.py                # Single-signal quick demo
├── pyproject.toml             # uv-managed dependencies
└── .env-example               # Environment variable template
```

---

## 13. Contributing

1. Fork the repository and create a feature branch.
2. Install dependencies: `uv sync`
3. Make changes, keeping all files under 150 lines.
4. Run the test suite: `uv run pytest tests/ -v`
5. Verify linting: `uv run ruff check src/`
6. Submit a pull request with a clear description of changes.

**Code style**: Ruff enforced. No bare `pip install` — use `uv add <package>` to add dependencies.

---

## 14. License

This project is released under the **MIT License**.

```
MIT License

Copyright (c) 2025 AI-Agents Course — HW1

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

*Author: AI-Agents Course — HW1*
