"""AirLLM error classes, constants, and module-level utility helpers."""

from __future__ import annotations

_SUPPORTED_COMPRESSIONS: set[str] = {"4bit", "8bit"}


class RunnerError(RuntimeError):
    """Raised when AirLLMRunner encounters a load or inference failure."""


class UnsupportedQuantError(RunnerError):
    """Raised when the requested quantization level is not supported by AirLLM."""


def _cuda_available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except Exception:
        return False


def _airllm_version() -> str:
    try:
        import airllm

        return getattr(airllm, "__version__", "unknown")
    except Exception:
        return "not installed"
