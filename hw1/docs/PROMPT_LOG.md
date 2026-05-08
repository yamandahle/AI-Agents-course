# Prompt Engineering Log — HW1: Signal Source Separation

**Project:** RNN/LSTM Sine Wave Source Separation  
**Version:** 1.00  
**Date:** 2026-05-08  
**Course:** AI Agents — Dr. Yoram Segal

---

## Overview

This log documents all AI-assisted prompts used during the development of HW1.
Each entry includes the prompt intent, the query issued, and the output/decision taken.

---

## Session 1 — Architecture Design & PRD

### Prompt 1.1 — Initial Requirements Analysis
**Intent:** Understand the homework requirements and design the system architecture.  
**Query:**
> "I have a homework on signal source separation using RNN, LSTM, and FC models.
> The task is: given noisy S5 (mixture of 4 sine waves) + a one-hot vector, reconstruct
> the clean individual sine wave. Help me design the data pipeline and model architecture."

**Output:** Defined the three-layer architecture (SDK models, services, entry points).
Chose BaseModel abstract class with save/load, SineDataset with input shape (W+4,),
and target shape (W,). Decided on sliding window with stride=1.

---

### Prompt 1.2 — PRD Creation
**Intent:** Write a formal requirements document.  
**Query:**
> "Write a PRD for this homework covering signals (S1–S4, S5), noise formula,
> dataset spec, model architectures (FC, RNN, LSTM), training config, and KPIs."

**Output:** `docs/PRD.md` — defines signal math, noise model σ~N(0,1) per window,
dataset split 80/20, training: MSE, Adam lr=0.001, epochs=50, batch=64.

---

## Session 2 — Data Pipeline Implementation

### Prompt 2.1 — Dataset Design
**Intent:** Implement efficient windowing using NumPy.  
**Query:**
> "Implement SineDataset using numpy.lib.stride_tricks.sliding_window_view for
> fast vectorised windowing. Input shape (W+4,) with one-hot + noisy S5 window.
> Target shape (W,) clean individual signal. Normalize each signal to [-1, 1]."

**Output:** `src/services/data_generator.py` — `SignalGenerator`, `SineDataset`,
`build_datasets` with 80/20 split and seed=42. Build time ~0.06 s.

---

### Prompt 2.2 — Noise Model Clarification
**Intent:** Clarify per-window vs per-signal noise resampling.  
**Query:**
> "The noise formula is y_noisy = (A + alpha*σ)*sin(2π*f*t + φ + beta*σ).
> Should σ be resampled per window or per full signal?"

**Output:** Per-window resampling — σ is drawn fresh for each call to
`noisy_s5_window()`. This makes consecutive windows statistically independent,
which is more realistic for training.

---

## Session 3 — Model Implementations

### Prompt 3.1 — RNN Architecture Choice
**Intent:** Design the RNN that uses the one-hot vector as the initial hidden state.  
**Query:**
> "Design SignalRNN where the one-hot vector (size 4) is projected to hidden_size=128
> via Linear(4, 128) and used as h0 for a 2-layer RNN. The noisy window (W,1) is the
> sequence input. Output: Linear(128, W) on the last hidden state."

**Output:** `src/sdk/models/rnn.py` — one-hot→Linear(4,128)→h0 for both layers,
RNN(input_size=1, hidden_size=128, num_layers=2, batch_first=True),
last hidden state (layer -1) → Linear(128, W).

---

### Prompt 3.2 — LSTM vs RNN Difference
**Intent:** Understand what extra code LSTM needs vs RNN.  
**Query:**
> "LSTM needs both h0 and c0. The one-hot vector projects to 128.
> Should h0 and c0 share the same projection weights or have separate Linear layers?"

**Output:** Separate Linear layers for h0 and c0 (`self.h0_proj` and `self.c0_proj`),
each Linear(4, 128). This gives LSTM two independent initial states, which is more
expressive than weight-sharing.

---

## Session 4 — Training & Experiments

### Prompt 4.1 — Training Loop Design
**Intent:** Implement the training loop with val MSE tracking.  
**Query:**
> "Write train_model(model, train_ds, val_ds, config) that returns a dict with
> train_losses, val_losses, best_val_mse, best_epoch. Use MSE loss, Adam, batch_size=64."

**Output:** `src/services/train.py` — per-epoch train and val loops, best model
tracking via `best_val_mse`. Returns full loss histories for plotting.

---

### Prompt 4.2 — Experiment Matrix Decision
**Intent:** Determine which dimensions to sweep in the experiment.  
**Query:**
> "Should we sweep window sizes (5, 10, 20) or fix W=10? The lecturer specified W=10.
> Should we include medium noise (α=β=0.1) or just low/high?"

**Output:** Fixed W=10 per lecturer requirement. Excluded medium noise to keep the
experiment matrix manageable (6 training runs instead of 27). This matches the
lecture requirement while still showing noise sensitivity.

---

## Session 5 — Enhancement Experiments

### Prompt 5.1 — FFT Spectral Analysis
**Intent:** Show that models recover the correct frequency, not just a smooth curve.  
**Query:**
> "For each signal S1–S4, plot the FFT magnitude spectrum comparing: clean target,
> noisy S5 input, and predictions from FC/RNN/LSTM. Use log scale on y-axis.
> This proves source separation, not just denoising."

**Output:** FFT plots saved as `outputs/figures/Sx_fft_comparison.png` for each
of the 4 signals. Key insight: a sharp peak at the signal's frequency in the
prediction confirms correct frequency extraction.

---

### Prompt 5.2 — RNN Epochs Experiment Design
**Intent:** Compare RNN convergence at 50 vs 100 epochs vs LSTM and FC.  
**Query:**
> "Create run_rnn_epochs.py that trains a fresh RNN for 100 epochs and compares
> its loss curve against FC and LSTM (50 epochs each). Show that RNN improves
> with more epochs but still doesn't match LSTM convergence."

**Output:** `run_rnn_epochs.py` — trains RNN-100ep, loads FC and LSTM loss
histories from results.json, plots 4 curves on one figure.
Finding: LSTM converges ~2× faster than RNN due to its cell state memory.

---

### Prompt 5.3 — Winner Heatmap Design
**Intent:** Summarise which model wins per signal/noise combination at a glance.  
**Query:**
> "Create a 2×4 heatmap (noise level × signal) where each cell is color-coded
> by the winning model (FC=blue, RNN=orange, LSTM=magenta) and annotated with
> the best MSE. Replace the 4 per-signal MSE bar charts with this single figure."

**Output:** `winner_heatmap.png` — generated in `run_figures.py`.
Key finding: FC wins most cases at low noise; LSTM is more robust at high noise.

---

## Session 6 — Code Quality & Testing

### Prompt 6.1 — Test Suite Design
**Intent:** Write unit tests covering all SDK models, data pipeline, and training.  
**Query:**
> "Write pytest tests for: (1) forward pass shapes for FC/RNN/LSTM, (2) save/load
> round-trip, (3) no NaN in outputs, (4) dataset structure, (5) training loop keys
> and loss decrease. Target: 37 tests, 0 Ruff errors."

**Output:** 55 tests across 4 test files with 97% coverage.
All tests pass; 0 Ruff errors.

---

### Prompt 6.2 — Coverage Gap Fix
**Intent:** Bring coverage from 59% to ≥85% by testing uncovered modules.  
**Query:**
> "experiment_runner.py and research_visualizer.py have 0% coverage.
> Write tests using unittest.mock.patch to mock train_model and build_datasets
> in run_experiments(). Test save_results, ExperimentResult, and all visualizer methods."

**Output:** `tests/unit/test_experiment_runner.py` and `tests/unit/test_visualizer.py`
— 18 new tests bringing total coverage to 97%.

---

## Summary

| Session | Area | Key Decision |
|---------|------|-------------|
| 1 | Architecture | SDK pattern — models in src/sdk/, services in src/services/ |
| 2 | Data pipeline | Per-window noise resampling; stride_tricks for fast windowing |
| 3 | Models | Separate h0/c0 projections for LSTM; one-hot as initial hidden state |
| 4 | Training | Fixed W=10, low/high noise only, 100 epochs |
| 5 | Enhancements | FFT analysis + epochs experiment + winner heatmap |
| 6 | Quality | 97% test coverage; 0 Ruff errors |

---

*All AI interactions used Claude Sonnet 4.6 via Claude Code CLI.*
