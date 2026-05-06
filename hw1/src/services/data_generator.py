import numpy as np
import torch
from typing import Tuple, List

class SignalGenerator:
    """Generates 1000Hz signals based on PRD mathematical foundations."""
    
    def __init__(self, config: dict):
        self.fs = config["signal"]["sampling_rate_hz"]
        self.duration = config["signal"]["duration_seconds"]
        self.freqs = config["signal"]["frequencies_hz"]
        self.sigma = config["signal"]["noise"]["sigma"]
        self.sigma_2 = config["signal"]["noise"]["sigma_2"]
        self.window_size = config["data"]["window_size"]

    def generate_signal(self, freq_idx: int) -> np.ndarray:
        """
        Implements: (A ± sigma)(sin(2pi * f * t + phi + sigma_2))
        """
        f = self.freqs[freq_idx]
        t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        phi = np.random.uniform(0, 2 * np.pi)
        
        # Amplitude noise (A=1)
        amp_noise = 1.0 + np.random.normal(0, self.sigma, t.shape)
        # Phase noise
        phase_noise = np.random.normal(0, self.sigma_2, t.shape)
        
        signal = amp_noise * np.sin(2 * np.pi * f * t + phi + phase_noise)
        return signal

    def create_dataset(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Creates a balanced dataset with 1-hot frequency encoding."""
        all_x, all_y = [], []
        
        for idx in range(len(self.freqs)):
            signal = self.generate_signal(idx)
            x, y = self._window_signal(signal, idx)
            all_x.append(x)
            all_y.append(y)
            
        return torch.cat(all_x), torch.cat(all_y)

    def _window_signal(self, signal: np.ndarray, freq_idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Creates 10-sample context windows with 1-hot encoding."""
        num_windows = len(signal) - self.window_size
        x_windows, y_targets = [], []
        
        # 1-hot encoding for frequency
        one_hot = np.zeros(len(self.freqs))
        one_hot[freq_idx] = 1.0
        
        for i in range(num_windows):
            window = signal[i : i + self.window_size]
            target = signal[i + self.window_size]
            
            # Concatenate window (10) + 1-hot (4) = 14 features
            features = np.concatenate([window, one_hot])
            x_windows.append(features)
            y_targets.append(target)
            
        return (torch.tensor(np.array(x_windows), dtype=torch.float32), 
                torch.tensor(np.array(y_targets), dtype=torch.float32).view(-1, 1))

if __name__ == "__main__":
    import json
    with open("config/setup.json", "r") as f:
        conf = json.load(f)
    gen = SignalGenerator(conf)
    x, y = gen.create_dataset()
    print(f"Dataset created. X shape: {x.shape}, Y shape: {y.shape}")
    # X shape should be (approx 40000, 14) -> 4 freqs * (10000 - 10) windows
