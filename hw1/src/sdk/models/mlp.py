import torch.nn as nn

class MLP(nn.Module):
    """
    Multi-Layer Perceptron for signal reconstruction.
    Features: 10 context samples + 4 one-hot frequency encoding bits.
    """
    def __init__(self, input_size: int = 14, layers: list = [128, 256, 128]):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, layers[0]),
            nn.ReLU(),
            nn.Linear(layers[0], layers[1]),
            nn.ReLU(),
            nn.Linear(layers[1], layers[2]),
            nn.ReLU(),
            nn.Linear(layers[2], 1)
        )

    def forward(self, x):
        """Standard feed-forward pass."""
        return self.net(x)
