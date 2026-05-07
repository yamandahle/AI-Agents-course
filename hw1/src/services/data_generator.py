import numpy as np
import torch
from torch.utils.data import Dataset, random_split
from typing import Tuple

NUM_SIGNALS = 5  # S1, S2, S3, S4, S5


class SignalGenerator:
    """Generates clean and noisy sine wave signals per PRD spec."""

    def __init__(self, config: dict):
        sig = config["signal"]
        self.freqs = sig["frequencies"]
        self.A = sig["amplitude"]
        self.phase = sig["phase"]
        self.t = np.linspace(
            0, sig["duration"],
            int(sig["sample_rate"] * sig["duration"]), endpoint=False
        )

    def clean(self, freq_idx: int) -> np.ndarray:
        """Returns full clean signal. freq_idx=4 → S5 (sum of S1–S4)."""
        if freq_idx == 4:
            return sum(
                self.A * np.sin(2 * np.pi * f * self.t + self.phase)
                for f in self.freqs
            )
        f = self.freqs[freq_idx]
        return self.A * np.sin(2 * np.pi * f * self.t + self.phase)

    def noisy_window(self, freq_idx: int, start: int, W: int,
                     alpha: float, beta: float) -> np.ndarray:
        """
        y_noisy = (A + alpha*σ) * sin(2π*f*t + phase + beta*σ)
        σ ~ N(0,1) re-sampled once per window.
        """
        t_win = self.t[start:start + W]
        sigma = float(np.random.normal(0, 1))
        if freq_idx == 4:
            return sum(
                (self.A + alpha * sigma) * np.sin(
                    2 * np.pi * f * t_win + self.phase + beta * sigma
                ) for f in self.freqs
            )
        f = self.freqs[freq_idx]
        return (self.A + alpha * sigma) * np.sin(
            2 * np.pi * f * t_win + self.phase + beta * sigma
        )


class SineDataset(Dataset):
    """Windowed sine dataset: input (W+5,), target (W,)."""

    def __init__(self, config: dict, noise_level: str, window_size: int):
        noise = config["noise"][noise_level]
        alpha, beta = noise["alpha"], noise["beta"]
        np.random.seed(config["data"]["seed"])

        gen = SignalGenerator(config)
        inputs, targets = [], []

        for sig_idx in range(NUM_SIGNALS):
            clean_full = gen.clean(sig_idx)
            norm = float(np.max(np.abs(clean_full))) or 1.0
            clean_norm = clean_full / norm

            one_hot = np.zeros(NUM_SIGNALS, dtype=np.float32)
            one_hot[sig_idx] = 1.0

            for i in range(len(clean_norm) - window_size):
                noisy_win = gen.noisy_window(sig_idx, i, window_size, alpha, beta) / norm
                clean_win = clean_norm[i:i + window_size]
                inputs.append(np.concatenate([one_hot, noisy_win]))
                targets.append(clean_win)

        self.X = torch.tensor(np.array(inputs), dtype=torch.float32)
        self.Y = torch.tensor(np.array(targets), dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.Y[idx]


def build_datasets(config: dict, noise_level: str,
                   window_size: int) -> Tuple[Dataset, Dataset]:
    """Returns (train_dataset, test_dataset) with 80/20 split."""
    full = SineDataset(config, noise_level, window_size)
    n_train = int(len(full) * config["data"]["train_ratio"])
    generator = torch.Generator().manual_seed(config["data"]["seed"])
    return random_split(full, [n_train, len(full) - n_train], generator=generator)
