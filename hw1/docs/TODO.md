# TODO — HW1: Signal Reconstruction

Status: `[ ]` = pending · `[x]` = done · `[~]` = in progress

---

## Phase 1 — Infrastructure & Config

- [x] Create `docs/PRD.md` (requirements, signals, models, experiment matrix, KPIs)
- [x] Create `docs/PLAN.md` (architecture, project structure, model specs, phases)
- [x] Create `docs/TODO.md` (this file)
- [x] Edit `config/setup.json` with all correct values (frequencies, noise presets, window sizes, training params)
- [x] Create `.gitignore` (exclude `__pycache__`, `*.pyc`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`)
- [x] Create `.env-example` (environment variable template)
- [x] Create `outputs/.gitkeep`, `outputs/figures/`, `outputs/results/`
- [x] Run `uv add torch numpy scipy matplotlib seaborn pandas`
- [x] Run `uv add --dev pytest pytest-cov ruff`

---

## Phase 2 — Data Service

- [x] Implement `src/services/data_generator.py`:
  - [x] `SignalGenerator`: clean sine arrays for S1–S4 and S5 sum
  - [x] One-hot encoding: size **4** (one entry per signal S1–S4)
  - [x] `noisy_s5_window`: σ re-sampled fresh per window (not per full signal)
  - [x] Normalize each signal to [-1, 1] before windowing
  - [x] Vectorised dataset using `numpy.lib.stride_tricks.sliding_window_view` (~0.06 s build)
- [x] `SineDataset`: input shape `(W+4,)`, target shape `(W,)`
- [x] `build_datasets`: 80/20 train/val split, all 4 signals in both splits, seed=42
- [x] Write `tests/unit/test_signals.py` (signal shapes, S5 formula, noise formula, dataset structure)

---

## Phase 3 — SDK Models

- [x] Create `src/sdk/models/base.py` (abstract `BaseModel`: `save`, `load`)
- [x] Create `src/sdk/models/fc.py` (`FC`):
  - [x] Input shape `(W+4,)` — one-hot (4) + noisy window (W)
  - [x] Output shape `(W,)`
  - [x] Architecture: `Linear(W+4, 256) → ReLU → Linear(256, 256) → ReLU → Linear(256, W)`
- [x] Create `src/sdk/models/rnn.py` (`SignalRNN`):
  - [x] one-hot (4) → `Linear(4, 128)` → h0 shape `(num_layers, batch, 128)`
  - [x] `RNN(input_size=1, hidden_size=128, num_layers=2, batch_first=True)`
  - [x] last hidden state → `Linear(128, W)` → output `(W,)`
- [x] Create `src/sdk/models/lstm.py` (`SignalLSTM`):
  - [x] one-hot (4) → `Linear(4, 128)` → h0 and c0
  - [x] `LSTM(input_size=1, hidden_size=128, num_layers=2, batch_first=True)`
  - [x] last output step → `Linear(128, W)` → output `(W,)`
- [x] Write `tests/unit/test_models.py` (forward pass shapes for all 3 models, save/load, no NaN)

---

## Phase 4 — Training Pipeline

- [x] Implement `src/services/train.py`:
  - [x] Loss: MSE
  - [x] Optimizer: Adam, lr=0.001
  - [x] Epochs: 50, batch size: 64
  - [x] Target shape `(W,)` not scalar
  - [x] Record train loss + val loss per epoch
  - [x] Track best validation MSE + best epoch
- [x] Write `tests/unit/test_trainer.py` (keys, loss length, loss decreases, best epoch in range, no NaN)

---

## Phase 5 — Experiments & Results

- [x] Create `src/services/experiment_runner.py`:
  - [x] `ExperimentResult` dataclass (signal, noise, window, model, train_losses, val_losses, best_mse, best_epoch)
  - [x] `save_results`: serialises list of ExperimentResult to `outputs/results/results.json`
  - [x] Experiment matrix: 4 signals × 2 noise levels × 1 window (W=10) × 3 models = **24 entries**
- [x] `outputs/results/results.json` exists with 24 entries

---

## Phase 6 — Reporting & Visualizations

- [x] `run_all.py` generates all 17 figures:

  **Signal inspection**
  - [x] `signals_overview.png` — all 4 sinusoids + S5 mixture on 2-panel figure

  **Per-signal figures (×4 signals)**
  - [x] `Sx_clean_vs_noisy.png` — clean target vs noisy S5 input
  - [x] `Sx_reconstruction.png` — 3-panel: one subplot per model with predictions
  - [x] `Sx_loss_curves.png` — train + val loss curves (log scale) for all 3 models
  - [x] ~~`Sx_mse_bar.png`~~ — **removed**, replaced by winner heatmap (E3)

  - [x] All base plots saved as PNG via `plt.savefig()` — no `plt.show()` anywhere

---

## Phase 7 — SDK Architecture

- [x] `src/sdk/models/` — FC, RNN, LSTM with shared `BaseModel` interface
- [x] `src/services/` — data generation, training, experiment runner (all business logic)
- [x] `run_all.py` — train all models, save to `outputs/models/`, save `results.json`, print tables
- [x] `run_figures.py` — load saved models + results → generate all 19 figures (no retraining)
- [x] `run_rnn_epochs.py` — standalone RNN 50 vs 100 epochs experiment
- [x] `run_test.py` — quick single-signal demo entry point

---

## Phase 8 — Docs & README

- [x] `README.md` with:
  - [x] Task description and signal definitions with math formula
  - [x] Installation guide (step-by-step with `uv sync`)
  - [x] Usage instructions (`run_all.py`, `run_test.py` with env var)
  - [x] Configuration guide (all `setup.json` parameters explained)
  - [x] Architecture section (SDK layout + data flow diagram)
  - [x] Full results table (per-signal val MSE, all models, low+high noise)
  - [x] Deep analysis: S4 easiest, FC vs LSTM noise sensitivity, RNN vanishing gradient, train/val MSE comparison
  - [x] All 17 figures embedded with captions
  - [x] Predictions table: more epochs / more layers / larger hidden size
  - [x] Testing section (37 tests, 0 Ruff errors)
  - [x] Contributing guidelines + MIT License
- [x] All source modules strictly under 150 lines

---

---

## Phase 9 — Enhancement Experiments (Understanding Demonstrations)

### E1 — FFT Spectral Analysis
- [x] For each signal S1–S4, compute `numpy.fft.rfft` on a representative window for the clean target, noisy S5 input, and each model's prediction
- [x] Plot magnitude spectrum (frequency axis) with 3 subplots (one per model) on a dark-theme figure
- [x] Save as `outputs/figures/Sx_fft_comparison.png` for each of the 4 signals
- [ ] Add FFT section to README analysis explaining what the spectrum reveals about model quality

### E2 — RNN Epochs Experiment (50 vs 100)
- [x] Create `run_rnn_epochs.py` — standalone script, does NOT re-run full training
- [x] Load RNN-50, LSTM-50, FC-50 loss histories from `outputs/results/results.json`
- [x] Train a fresh RNN for 100 epochs only (low noise, W=10)
- [x] Plot all 4 curves: RNN-50, RNN-100, LSTM-50, FC-50 on one figure
- [x] Save as `outputs/figures/rnn_epochs_comparison.png`
- [ ] Add analysis to README: "more epochs helps RNN but it still doesn't match LSTM"

### E3 — Model Winner Heatmap
- [x] Build 2×4 matrix (noise level × signal), each cell = name of best model + its MSE
- [x] Colour-code: blue=FC, orange=RNN, magenta=LSTM
- [x] Save as `outputs/figures/winner_heatmap.png`
- [ ] Reference heatmap in README summary section

---

## Quality Gates (all passing)

- [x] `uv run pytest tests/ -v` — **37 tests passing**
- [x] `uv run ruff check src/` — **0 errors**
- [x] `outputs/results/results.json` exists with **24 entries**
- [x] 13 base PNG figures saved in `outputs/figures/` (17 original minus 4 removed MSE bar charts)
- [ ] 6 enhancement PNG figures saved in `outputs/figures/` (4 FFT + 1 epochs + 1 heatmap)
- [x] No `plt.show()` anywhere in source
- [x] No hardcoded values in source modules — everything from `config/setup.json`
- [x] All source modules under 150 lines
- [x] `.env-example` present
