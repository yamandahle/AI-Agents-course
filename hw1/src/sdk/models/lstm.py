import torch
import torch.nn as nn

class SignalLSTM(nn.Module):
    """
    Long Short-Term Memory network implementing the gated memory formula.
    Concept: y = f_w(x) + memory (Cell State & Hidden State).
    """
    def __init__(self, input_size: int = 14, hidden_size: int = 256, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # Reshape (batch, 14) to (batch, 1, 14)
        if x.dim() == 2:
            x = x.unsqueeze(1)
            
        # out: (batch, seq, hidden), (h, c): Hidden and Cell states (memory)
        out, _ = self.lstm(x)
        
        return self.fc(out[:, -1, :])
