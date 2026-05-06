# HW1 - High-Frequency Signal Reconstruction (MLP, RNN, LSTM)

## 1. Project Overview
This project implements a robust machine learning pipeline to reconstruct high-frequency sine wave signals. The system evaluates the performance of three distinct architectures—**MLP, RNN, and LSTM**—in predicting the next sample based on a short context window, even in the presence of randomized noise.

### Mathematical Foundation
The input signal is synthesized using a noisy harmonic model to test architectural robustness:
**Equation:** `Signal = (A ± sigma) * (sin(2pi * f * t + phi + sigma_2))`
- **sigma:** Amplitude noise (0.1)
- **sigma_2:** Phase noise (0.05)
- **f:** One of four distinct frequencies (5Hz, 50Hz, 150Hz, 450Hz)

---

## 2. Architectural Map
The project adheres to a strict **SDK-based service architecture**, ensuring clean separation between model definitions and business logic.

### `src/sdk/models/` (The Core)
Contains modular, single-responsibility model definitions. Every file is strictly **under 150 lines**.
- **`mlp.py`**: A 3-layer fully connected network `[128, 256, 128]` for non-linear baseline reconstruction.
- **`rnn.py`**: A recurrent network implementing the PRD-mandated state logic.
- **`lstm.py`**: A gated recurrent network for long-term temporal dependency tracking.

### `src/services/` (The Logic)
- **`data_generator.py`**: Orchestrates 1000Hz signal synthesis and sliding window creation.
- **`train.py`**: Centralized training pipeline that validates models against MSE and latency KPIs.

---

## 3. Mathematical Core: Recurrent State
All recurrent models (RNN and LSTM) are designed to satisfy the state transformation requirement:
**`y = f_w(x) + memory`**
- **`f_w(x)`**: Transformation of the current 10-sample context window concatenated with a 4-item 1-hot frequency vector.
- **`memory`**: The hidden state (RNN) or cell state (LSTM) that persists temporal information across the sequence.

---

## 4. Reproducibility
The project uses `uv` for lightning-fast, reproducible dependency management.

### Setup
```bash
# Install dependencies
uv add numpy torch
```

### Execution
To ensure proper module resolution, always run commands from the project root using the `PYTHONPATH=.` prefix:

**Data Verification:**
```bash
PYTHONPATH=. uv run python src/services/data_generator.py
```

**Model Training:**
```bash
PYTHONPATH=. uv run python src/services/train.py
```

---

## 5. Strict Constraints & Compliance
This project was developed under high-precision engineering constraints:
- **Sampling Rate:** 1000Hz (Strict 1ms sampling period).
- **Signal Duration:** 10 seconds (10,000 samples per frequency type).
- **Modularity:** **Every source file is < 150 lines**.
- **Context Window:** Exactly 10 samples for the look-back period.
- **Target Accuracy:** MSE targets (MLP < 0.005, RNN < 0.002, LSTM < 0.001) driven by 200 training epochs.

---
**Author:** AI-Agents Course - HW1 Implementation
**Status:** Verified & DNA-Compliant
