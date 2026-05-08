import numpy as np
import torch
from torch.utils.data import Dataset, random_split
from typing import Tuple

NUM_SIGNALS = 4  # S1, S2, S3, S4 (S5 = mixture, always the model input)


class SignalGenerator:
    """Generates clean and noisy signals for source separation.

    Task: given noisy S5 window + one_hot(4) → reconstruct clean Si window.
    """

    def __init__(self, config: dict):
        """Read signal parameters from config and pre-compute the time axis and random phases."""
        sig = config["signal"]
        self.freqs = sig["frequencies"]   # [1, 2, 5, 10]
        self.A = sig["amplitude"]
        n = int(sig["sample_rate"] * sig["duration"])
        self.t = np.linspace(0, sig["duration"], n, endpoint=False)
        # Deterministic phases φ ~ Uniform(0, 2π), isolated from global seed
        rng = np.random.default_rng(config.get("data", {}).get("seed", 42))
        self.phases = rng.uniform(0, 2 * np.pi, NUM_SIGNALS)

    def clean(self, sig_idx: int) -> np.ndarray:
        """Clean individual signal Si (sig_idx 0–3)."""
        f = self.freqs[sig_idx]
        return self.A * np.sin(2 * np.pi * f * self.t + self.phases[sig_idx])

    def clean_s5(self) -> np.ndarray:
        """Clean mixture S5 = S1 + S2 + S3 + S4."""
        return sum(self.clean(i) for i in range(NUM_SIGNALS))

    def noisy_s5_window(self, start: int, W: int,
                        alpha: float, beta: float) -> np.ndarray:
        """Noisy S5 window — model input.
        y_noisy = Σᵢ (A + alpha*σ) * sin(2π*fᵢ*t + φᵢ + beta*σ)
        σ ~ N(0,1) re-sampled once per window.
        """
        t_win = self.t[start:start + W]
        sigma = float(np.random.normal(0, 1))
        return sum(
            (self.A + alpha * sigma) * np.sin(
                2 * np.pi * self.freqs[i] * t_win + self.phases[i] + beta * sigma
            )
            for i in range(NUM_SIGNALS)
        )

    def noisy_window(self, sig_idx: int, start: int, W: int,
                     alpha: float, beta: float) -> np.ndarray:
        """Noisy window of a single signal (visualization only)."""
        t_win = self.t[start:start + W]
        sigma = float(np.random.normal(0, 1))
        f = self.freqs[sig_idx]
        return (self.A + alpha * sigma) * np.sin(
            2 * np.pi * f * t_win + self.phases[sig_idx] + beta * sigma
        )


class SineDataset(Dataset):
    """Source separation dataset.
    Input:  (W+4,) = [one_hot(4)] + [noisy_S5_window(W)]
    Target: (W,)   = clean individual signal window
    """

    def __init__(self, config: dict, noise_level: str, window_size: int):
        """Build all windows for all 4 signals using vectorised stride_tricks."""
        noise = config["noise"][noise_level]
        alpha, beta = noise["alpha"], noise["beta"]
        np.random.seed(config["data"]["seed"])

        gen = SignalGenerator(config)
        W = window_size
        n = len(gen.t)
        n_wins = n - W

        # Normalize clean signals
        clean_sigs = []
        for i in range(NUM_SIGNALS):
            sig = gen.clean(i)
            norm = float(np.max(np.abs(sig))) or 1.0
            clean_sigs.append(sig / norm)
        clean_s5 = gen.clean_s5()
        norm_s5 = float(np.max(np.abs(clean_s5))) or 1.0

        # All t-windows at once: (n_wins, W)
        t_wins = np.lib.stride_tricks.sliding_window_view(gen.t, W)[:n_wins]

        # One sigma per window, broadcast over W: (n_wins, 1)
        sigmas = np.random.normal(0, 1, n_wins).astype(np.float32)[:, np.newaxis]

        # Vectorised noisy S5: (n_wins, W)
        noisy_s5 = np.zeros((n_wins, W), dtype=np.float32)
        for i in range(NUM_SIGNALS):
            noisy_s5 += ((gen.A + alpha * sigmas) * np.sin(
                2 * np.pi * gen.freqs[i] * t_wins + gen.phases[i] + beta * sigmas
            )).astype(np.float32)
        noisy_s5 /= norm_s5  # (n_wins, W)

        all_inputs, all_targets = [], []
        for sig_idx in range(NUM_SIGNALS):
            one_hot = np.zeros(NUM_SIGNALS, dtype=np.float32)
            one_hot[sig_idx] = 1.0
            one_hot_tiled = np.tile(one_hot, (n_wins, 1))            # (n_wins, 4)
            all_inputs.append(np.concatenate([one_hot_tiled, noisy_s5], axis=1))  # (n_wins, W+4)
            all_targets.append(
                np.lib.stride_tricks.sliding_window_view(clean_sigs[sig_idx], W)
                [:n_wins].astype(np.float32)
            )

        self.X = torch.tensor(np.concatenate(all_inputs, axis=0), dtype=torch.float32)
        self.Y = torch.tensor(np.concatenate(all_targets, axis=0), dtype=torch.float32)

    def __len__(self) -> int:
        """Return total number of (input, target) window pairs across all signals."""
        return len(self.X)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Return the (input, target) pair at position idx."""
        return self.X[idx], self.Y[idx]


def build_datasets(config: dict, noise_level: str,
                   window_size: int) -> Tuple[Dataset, Dataset]:
    """Returns (train_dataset, test_dataset) with 80/20 split."""
    full = SineDataset(config, noise_level, window_size)
    n_train = int(len(full) * config["data"]["train_ratio"])
    generator = torch.Generator().manual_seed(config["data"]["seed"])
    return random_split(full, [n_train, len(full) - n_train], generator=generator)
