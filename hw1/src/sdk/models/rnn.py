import torch
import torch.nn as nn

class SignalRNN(nn.Module):
    """
    Recurrent Neural Network implementing the state formula: y = f_w(x) + memory.
    """
    def __init__(self, input_size: int = 14, hidden_size: int = 128, num_layers: int = 2):
        super().__init__()
        # Internal RNN captures the y = f_w(x) + memory logic
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # Reshape (batch, 14) to (batch, 1, 14) for sequence processing
        if x.dim() == 2:
            x = x.unsqueeze(1)
        
        # out: (batch, seq, hidden), _ : hidden state (memory)
        out, _ = self.rnn(x)
        
        # Mapping hidden state (memory) to prediction
        return self.fc(out[:, -1, :])
