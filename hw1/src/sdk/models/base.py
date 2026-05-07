from abc import abstractmethod
import torch
import torch.nn as nn


class BaseModel(nn.Module):
    """Abstract base class for all signal reconstruction models."""

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...

    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)

    def load(self, path: str) -> None:
        self.load_state_dict(torch.load(path, weights_only=True))
