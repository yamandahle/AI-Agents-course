import torch
import torch.nn as nn
from src.sdk.models.base import BaseModel

NUM_SIGNALS = 5


class SignalRNN(BaseModel):
    """
    RNN for signal reconstruction.
    one_hot → Linear(5, hidden) → h0
    Input sequence: noisy_window reshaped to (batch, W, 1)
    Output: (W,) via last hidden state
    """

    def __init__(self, window_size: int, hidden_size: int = 128, num_layers: int = 2):
        super().__init__()
        self.num_layers = num_layers
        self.h0_proj = nn.Linear(NUM_SIGNALS, hidden_size)
        self.rnn = nn.RNN(1, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, window_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        one_hot = x[:, :NUM_SIGNALS]                # (batch, 5)
        window = x[:, NUM_SIGNALS:].unsqueeze(-1)   # (batch, W, 1)

        h0 = self.h0_proj(one_hot)                  # (batch, hidden)
        h0 = h0.unsqueeze(0).expand(self.num_layers, -1, -1).contiguous()

        _, hn = self.rnn(window, h0)                # hn: (layers, batch, hidden)
        return self.fc(hn[-1])                      # (batch, W)
