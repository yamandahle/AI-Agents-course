import torch.nn as nn
from src.sdk.models.base import BaseModel

NUM_SIGNALS = 4


class FC(BaseModel):
    """
    Fully Connected network for source separation.
    Input:  (W+4,) = [one_hot(4,), noisy_S5_window(W,)]
    Output: (W,)   = reconstructed clean individual signal window
    """

    def __init__(self, window_size: int, hidden: int = 256):
        """Build three-layer MLP; input_size = window_size + 4 one-hot features."""
        super().__init__()
        input_size = window_size + NUM_SIGNALS
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, window_size)
        )

    def forward(self, x):
        """Map flat input vector (W+4,) → clean signal window (W,)."""
        return self.net(x)
