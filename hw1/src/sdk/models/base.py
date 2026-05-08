from abc import abstractmethod
import torch
import torch.nn as nn


class BaseModel(nn.Module):
    """Abstract base class for all signal reconstruction models."""

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Run a forward pass; must be implemented by each subclass."""
        ...

    def save(self, path: str) -> None:
        """Persist model weights to disk at the given path."""
        torch.save(self.state_dict(), path)

    def load(self, path: str) -> None:
        """Restore model weights from a previously saved checkpoint."""
        self.load_state_dict(torch.load(path, weights_only=True))
