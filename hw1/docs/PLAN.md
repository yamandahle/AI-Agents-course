# Technical Development Plan - HW1: Signal Reconstruction

## 1. Primary Constraints & Standards
- **Sampling Rate:** 1000Hz (Strict requirement).
- **File Limit:** Every source file **MUST be under 150 lines**.
- **Context:** 10-sample sliding window.

## 2. Mathematical Implementation
### 2.1 Signal Reconstruction Formula
Implementation of data generation will follow:
`Signal = (A ± sigma)(sin(2pi * f * t + phi + sigma_2))`

### 2.2 Model State Logic
RNN and LSTM layers will implement:
`y = f_w(x) + memory`

## 3. Architectural Overview
The project follows a modular, SDK-based architecture to promote reusability and clean separation of concerns.

### 1.1 Core Components
- **`src/sdk/`**: Contains the foundational building blocks (model definitions, data primitives, and utility functions).
- **`src/services/`**: Orchestrates high-level business logic (Data Generation Service, Training/Inference Service).
- **`src/shared/`**: Common configurations, constants, and logging utilities.

## 2. Configuration-Driven Approach
All parameters (sampling rate, duration, model hyperparameters, noise levels) will be managed via a centralized configuration system.
- **`config/default.yaml`**: Primary configuration file.
- **`src/shared/config.py`**: Pydantic-based configuration loader and validator.

## 3. Service Breakdown

### 3.1 Data Generation Service (`src/services/data_gen/`)
- **Responsibility**: Generate 1000Hz signals with 1-hot frequency encoding and noise.
- **Key Modules**:
    - `generator.py`: Core signal math.
    - `noise.py`: Gaussian noise injection.
    - `exporter.py`: Saving signals to structured formats (Parquet/CSV).

### 3.2 Training Service (`src/services/training/`)
- **Responsibility**: Execute training loops for MLP, RNN, and LSTM.
- **Key Modules**:
    - `pipeline.py`: Main training orchestration.
    - `evaluator.py`: KPI calculation and comparison.
    - `checkpoint_manager.py`: Model serialization.

## 4. SDK Development (`src/sdk/`)
- **`src/sdk/models/`**: Separate files for `mlp.py`, `rnn.py`, and `lstm.py` (each < 150 lines).
- **`src/sdk/data/`**: `dataset.py` (PyTorch Dataset) and `transforms.py` (Windowing logic).

## 5. File Size Constraint Strategy
To strictly maintain files under 150 lines:
- **Modularization**: Large classes will be split using composition or mixins.
- **Utility Extraction**: Repetitive logic moved to `src/shared/utils/`.
- **Interface Segregation**: Complex logic decomposed into smaller, functional units.

## 6. Implementation Milestones

### Milestone 1: Infrastructure & Config (Day 1)
- Setup SDK structure and config loader.
- Implement 1-hot encoding utilities in `shared/`.

### Milestone 2: Data Service (Day 2)
- Build 1000Hz signal generator.
- Implement randomized noise and windowing transforms.

### Milestone 3: SDK Models (Day 3)
- Implement MLP, RNN, and LSTM in `src/sdk/models/`.
- Ensure each model file adheres to the 150-line limit.

### Milestone 4: Training Pipeline (Day 4)
- Build the service-level training loop.
- Integrate logging and checkpointing.

### Milestone 5: Evaluation & Comparison (Day 5)
- Implement KPI tracking (MSE, Latency).
- Generate comparative report.

## 7. Quality Assurance
- **Unit Testing**: 100% coverage for SDK components.
- **Integration Testing**: End-to-end verification of Signal Gen -> Train -> Eval.
- **Linting**: Strict ruff/black checks.
