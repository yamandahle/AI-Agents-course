# Product Requirements Document (PRD) - HW1: Signal Reconstruction

## 1. Project Overview
**Project Name:** HW1 - Multi-Architecture Signal Reconstruction
**Objective:** Develop and compare three distinct neural network architectures (MLP, RNN, and LSTM) to reconstruct/predict a high-frequency sine wave signal. The system must handle multiple frequencies distinguished by 1-hot encoding and maintain robustness against randomized noise.

## 2. Technical Constraints
- **Primary Constraint: Sampling Rate:** 1000Hz (1 sample per millisecond).
- **Primary Constraint: Modularity:** Every source code file must be **under 150 lines**.
- **Total Duration:** 10 seconds per signal (10,000 samples total).
- **Context Window:** 10-sample sliding window (look-back period).

## 3. Mathematical Foundations
### 3.1 Signal Generation
The input signal is generated using the following equation to incorporate randomized noise:
`Signal: (A ± sigma)(sin(2pi * f * t + phi + sigma_2))`
Where:
- `A`: Amplitude
- `f`: Frequency (one of 4 types)
- `phi`: Phase shift
- `sigma`, `sigma_2`: Randomized Gaussian noise components

### 3.2 RNN State Logic
The recurrent models will adhere to the following state representation:
`RNN State: y = f_w(x) + memory`
Where `f_w(x)` is the current input transformation and `memory` represents the hidden state/cell state.

## 4. Problem Statement
Accurate signal reconstruction in high-frequency environments is challenged by noise and varying signal characteristics. This project aims to evaluate how traditional feed-forward networks (MLP) compare against sequence-aware models (RNN, LSTM) when provided with a short context window and auxiliary frequency information.

## 4. Functional Requirements
### 4.1 Data Generation
- Generate 10-second sine waves at 1000Hz.
- Support 4 predefined frequencies.
- Implement 1-hot encoding for the frequency ID to be fed alongside the signal.
- Add adjustable randomized noise to the generated signals.

### 4.2 Preprocessing
- Implement a sliding window of 10 samples.
- Concatenate the 1-hot frequency vector to the input features.
- Normalize input data to a standard range (e.g., [0, 1] or [-1, 1]).

### 4.3 Model Implementation
- **MLP:** A deep feed-forward network as a baseline.
- **RNN:** A standard recurrent network to capture temporal dependencies.
- **LSTM:** A gated recurrent unit to handle long-term dependencies and gradient stability.

### 4.4 Training & Evaluation
- Implement a unified training pipeline for all three architectures.
- Support model-specific hyperparameters (hidden layers, neurons, dropout).
- Real-time logging of training/validation loss.

## 5. Non-Functional Requirements
- **Extensibility:** The architecture should allow for easy addition of new signal types or models.
- **Efficiency:** Training should complete within a reasonable timeframe on standard hardware.
- **Reproducibility:** Use fixed seeds for data generation and weight initialization.

## 6. Success KPIs (Key Performance Indicators)
| Metric | Target (MLP) | Target (RNN) | Target (LSTM) |
|--------|--------------|--------------|---------------|
| **Mean Squared Error (MSE)** | < 0.005 | < 0.002 | < 0.001 |
| **Inference Latency** | < 1ms | < 3ms | < 5ms |
| **Noise Robustness** | Base | +15% over MLP | +25% over MLP |
| **Training Stability** | High | Medium | High |

## 7. Delivery Artifacts
- Source code for all three models and the data generator.
- Comparative analysis report (actual vs. predicted for each model).
- Saved model checkpoints for the best performing iteration of each architecture.
