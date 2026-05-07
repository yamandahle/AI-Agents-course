import json
import os
import numpy as np
import torch
from dataclasses import dataclass, asdict
from typing import List
from src.services.data_generator import build_datasets
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.services.train import train_model

SIGNAL_NAMES = ["S1", "S2", "S3", "S4"]
MODEL_MAP = {"FC": FC, "RNN": SignalRNN, "LSTM": SignalLSTM}
N_EVAL = 200   # windows per signal for MSE evaluation


@dataclass
class ExperimentResult:
    signal:       str
    noise_level:  str
    window_size:  int
    model:        str
    best_mse:     float
    best_epoch:   int
    train_losses: List[float]
    val_losses:   List[float]


def _per_signal_mse(model, full_ds, sig_idx: int, W: int) -> float:
    """Evaluate MSE on N_EVAL windows of one signal from the full dataset."""
    n_per_sig = len(full_ds) // 4
    sig_start = sig_idx * n_per_sig
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for i in range(N_EVAL):
            x, y = full_ds[sig_start + i * W]
            preds.append(model(x.unsqueeze(0)).squeeze().numpy())
            targets.append(y.numpy())
    return float(np.mean((np.concatenate(preds) - np.concatenate(targets)) ** 2))


def run_experiments(config: dict, fast: bool = False) -> List[ExperimentResult]:
    """
    27 training runs (3 noise × 3 W × 3 models).
    Each model evaluated on all 4 signals → 108 result entries.
    """
    if fast:
        config = {**config, "training": {**config["training"], "epochs": 10}}

    noise_levels = list(config["noise"].keys())
    window_sizes = config["data"]["window_sizes"]
    results = []
    total_trains = len(noise_levels) * len(window_sizes) * len(MODEL_MAP)
    run = 0

    for noise in noise_levels:
        for W in window_sizes:
            train_ds, val_ds = build_datasets(config, noise, window_size=W)
            full_ds = val_ds.dataset
            for model_name, ModelClass in MODEL_MAP.items():
                run += 1
                print(f"[{run}/{total_trains}] noise={noise} W={W} model={model_name}")
                model = ModelClass(W)
                res = train_model(model, train_ds, val_ds, config)
                for sig_idx, sig_name in enumerate(SIGNAL_NAMES):
                    mse = _per_signal_mse(model, full_ds, sig_idx, W)
                    results.append(ExperimentResult(
                        signal=sig_name,
                        noise_level=noise,
                        window_size=W,
                        model=model_name,
                        best_mse=mse,
                        best_epoch=res["best_epoch"],
                        train_losses=res["train_losses"],
                        val_losses=res["val_losses"],
                    ))
    return results


def save_results(results: List[ExperimentResult], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"Saved {len(results)} results → {path}")
