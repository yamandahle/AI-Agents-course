import torch
import torch.nn as nn
from src.sdk.models.base import BaseModel

NUM_SIGNALS = 4


class SignalLSTM(BaseModel):
    """
    LSTM for source separation.
    one_hot → Linear(4, hidden) → h0 and c0
    Input sequence: noisy_S5_window reshaped to (batch, W, 1)
    Output: (W,) via last output step
    """

    def __init__(self, window_size: int, hidden_size: int = 128, num_layers: int = 2):
        """Build LSTM with separate h0/c0 projections from the one-hot signal index."""
        super().__init__()
        self.num_layers = num_layers
        self.h0_proj = nn.Linear(NUM_SIGNALS, hidden_size)
        self.c0_proj = nn.Linear(NUM_SIGNALS, hidden_size)
        self.lstm = nn.LSTM(1, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, window_size)

    def forward(self, x: torch.Tensor, return_states: bool = False) -> torch.Tensor:
        """Encode one-hot into h0 and c0, run LSTM, decode last output step."""
        one_hot = x[:, :NUM_SIGNALS]                # (batch, 4)
        window = x[:, NUM_SIGNALS:].unsqueeze(-1)   # (batch, W, 1)

        h0 = self.h0_proj(one_hot).unsqueeze(0).expand(self.num_layers, -1, -1).contiguous()
        c0 = self.c0_proj(one_hot).unsqueeze(0).expand(self.num_layers, -1, -1).contiguous()

        out, (hn, cn) = self.lstm(window, (h0, c0)) # out: (batch, W, hidden)
        preds = self.fc(out[:, -1, :])              # (batch, W)
        
        if return_states:
            return preds, out # 'out' in LSTM contains all hidden states h_t
        return preds
