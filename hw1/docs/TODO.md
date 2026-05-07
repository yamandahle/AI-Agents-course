# TODO — HW1: Signal Reconstruction

Status: `[ ]` = pending · `[x]` = done · `[~]` = in progress

---

## Phase 1 — Infrastructure & Config

- [ ] Create `configs/signals.json` (frequencies, amplitude, phase, duration, sample_rate)
- [ ] Create `configs/noise.json` (low/med/high alpha+beta presets)
- [ ] Create `configs/training.json` (epochs, batch_size, lr, window_sizes, train_ratio, seed)
- [ ] Create `configs/models.json` (hidden_size, num_layers, fc_hidden)
- [ ] Create `.gitignore` (exclude `__pycache__`, `*.pyc`, `outputs/figures/`, `outputs/results/`, `.venv/`)
- [ ] Create `outputs/.gitkeep`, `outputs/figures/`, `outputs/results/`
- [ ] Run `uv add torch numpy scipy matplotlib seaborn pandas`
- [ ] Run `uv add --dev pytest pytest-cov ruff`

---

## Phase 2 — Data Service

- [ ] Fix `src/services/data_generator.py`:
  - [ ] Add S5 signal (sum of S1+S2+S3+S4)
  - [ ] Change one-hot encoding size from 4 → 5
  - [ ] Ensure σ is re-sampled fresh per window (not per full signal)
  - [ ] Normalize signals to [-1, 1] before windowing
- [ ] Add sliding window builder (stride=1, outputs `(W+5,)` input + `(W,)` target pairs)
- [ ] Add train/test split (80/20, all 5 signals in both splits, seed=42)
- [ ] Write `tests/unit/test_signals.py` (signal shapes, S5 formula, noise formula)

---

## Phase 3 — SDK Models

- [ ] Create `src/sdk/models/base.py` (abstract BaseModel: fit, predict, save, load)
- [ ] Fix `src/sdk/models/mlp.py`:
  - [ ] Input shape `(W+5,)` — concatenation of one-hot + noisy window
  - [ ] Output shape `(W,)` — not 1 sample
  - [ ] Architecture: `Linear(W+5, 256) → ReLU → Linear(256, 256) → ReLU → Linear(256, W)`
- [ ] Fix `src/sdk/models/rnn.py`:
  - [ ] one-hot → `Linear(5, 128)` → h0 shape `(2, batch, 128)`
  - [ ] `RNN(input_size=1, hidden_size=128, num_layers=2, batch_first=True)`
  - [ ] last hidden state → `Linear(128, W)` → output `(W,)`
- [ ] Fix `src/sdk/models/lstm.py`:
  - [ ] one-hot → `Linear(5, 128)` → h0 and c0
  - [ ] `LSTM(input_size=1, hidden_size=128, num_layers=2, batch_first=True)`
  - [ ] last output step → `Linear(128, W)` → output `(W,)`
- [ ] Write `tests/unit/test_models.py` (forward pass shapes for all 3 models)

---

## Phase 4 — Training Pipeline

- [ ] Fix `src/services/train.py`:
  - [ ] Loss: MSE
  - [ ] Optimizer: Adam, lr=0.001
  - [ ] Epochs: 50, batch size: 64
  - [ ] Target shape `(W,)` not scalar
  - [ ] Record train loss + val loss per epoch
  - [ ] Track best validation MSE + best epoch
- [ ] Write `tests/unit/test_trainer.py` (train 1 epoch, loss decreases, shapes correct)

---

## Phase 5 — Experiments & Results

- [ ] Create `src/services/experiment_runner.py`:
  - [ ] Cartesian product loop: 5 signals × 3 noise levels × 3 window sizes × 3 models = 135 runs
  - [ ] Load all params from `configs/*.json`
  - [ ] Save each run result to list
- [ ] Create `src/services/results_collector.py`:
  - [ ] ExperimentResult dataclass (signal, noise, window, model, train_losses, val_losses, best_mse, best_epoch)
  - [ ] Save all 135 results to `outputs/results/results.json`
- [ ] Write `tests/integration/test_experiments.py` (run 1 mini experiment, check results.json structure)

---

## Phase 6 — Reporting & Visualizations

- [ ] Fix/expand `src/services/research_visualizer.py`:

  **Signal inspection plots**
  - [ ] Plot all 5 clean signals (S1–S5) on one figure — verify shapes and frequencies
  - [ ] Plot clean vs noisy for each noise level (low/med/high) — 1 signal × 3 noise levels

  **Reconstruction plots (per model)**
  - [ ] For each model (MLP, RNN, LSTM): plot noisy input vs clean target vs model prediction on same axes
  - [ ] Save as `outputs/figures/reconstruction_mlp.png`, `reconstruction_rnn.png`, `reconstruction_lstm.png`

  **Loss curves**
  - [ ] For each model: plot train loss and val loss vs epoch (50 epochs) on same axes
  - [ ] Save as `outputs/figures/loss_mlp.png`, `loss_rnn.png`, `loss_lstm.png`

  **Model comparison**
  - [ ] Bar chart: best validation MSE per model (MLP vs RNN vs LSTM) — one bar per model
  - [ ] Save as `outputs/figures/model_comparison_bar.png`

  **Effect of noise level**
  - [ ] Line plot: MSE vs noise level (low/med/high) — one line per model
  - [ ] Save as `outputs/figures/noise_effect.png`

  **Effect of window size**
  - [ ] Line plot: MSE vs window size (W=5/10/20) — one line per model
  - [ ] Save as `outputs/figures/window_effect.png`

  **Effect of signal type**
  - [ ] Bar chart: MSE per signal (S1–S5) grouped by model — shows which signal is hardest
  - [ ] Save as `outputs/figures/signal_effect.png`

  **Heatmap**
  - [ ] MSE heatmap: rows = signals (S1–S5), cols = noise levels, one heatmap per model
  - [ ] Save as `outputs/figures/heatmap_mlp.png`, `heatmap_rnn.png`, `heatmap_lstm.png`

  - [ ] All plots saved as PNG via `plt.savefig()` — no `plt.show()` anywhere

---

## Phase 7 — SDK + Integration

- [ ] Create `src/sdk/hw1_sdk.py` (HW1SDK class wrapping all services)
- [ ] Create `src/sdk/__init__.py` (exports HW1SDK)
- [ ] Create `tests/conftest.py` (shared fixtures: tiny_config, dummy_signal, tmp_dir)
- [ ] Write `tests/integration/test_sdk.py` (SDK imports clean, runs end-to-end)
- [ ] Run `uv run pytest --cov=src --cov-fail-under=85`
- [ ] Run `uv run ruff check src/` — fix all errors

---

## Phase 8 — Docs & README

- [ ] Expand `README.md` with:
  - [ ] Project description and signal definitions
  - [ ] How to install and run (`uv sync`, `uv run python main.py`)
  - [ ] Reconstruction plots (embedded PNGs)
  - [ ] Comparison table (45 rows × 3 models)
  - [ ] Analysis: which model performs best and why
- [ ] Verify all source files are under 150 lines
- [ ] Mark completed tasks in this file

---

## Quality Gates (must pass before submission)

- [ ] `uv run pytest --cov=src --cov-fail-under=85` — coverage ≥ 85%
- [ ] `uv run ruff check src/` — zero errors
- [ ] `outputs/results/results.json` exists with 135 entries
- [ ] At least 1 reconstruction plot per model saved in `outputs/figures/`
- [ ] No `plt.show()` anywhere in source
- [ ] No hardcoded values — everything from `configs/*.json`
- [ ] All source files strictly under 150 lines
