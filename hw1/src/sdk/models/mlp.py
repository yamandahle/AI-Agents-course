import torch.nn as nn
from src.sdk.models.base import BaseModel

NUM_SIGNALS = 5


class MLP(BaseModel):
    """
    MLP for signal reconstruction.
    Input:  (W+5,) = [one_hot(5,), noisy_window(W,)]
    Output: (W,)   = reconstructed clean window
    """

    def __init__(self, window_size: int, hidden: int = 256):
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
        return self.net(x)
