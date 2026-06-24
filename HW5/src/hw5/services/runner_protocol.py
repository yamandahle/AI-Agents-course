"""RunnerProtocol and InferenceResult — shared interface for all framework runners."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from hw5.shared.quant_config import QuantizationConfig


@dataclass
class InferenceResult:
    """Timing and output from a single model inference call."""

    output_text: str
    tokens_generated: int
    total_time_s: float
    first_token_latency_s: float
    framework: str
    model_id: str
    quant: str
    prompt_token_count: int = 0
    tokens_per_sec: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.tokens_per_sec == 0.0 and self.total_time_s > 0:
            self.tokens_per_sec = self.tokens_generated / self.total_time_s

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible plain dictionary."""
        return {
            "output_text": self.output_text,
            "tokens_generated": self.tokens_generated,
            "total_time_s": self.total_time_s,
            "first_token_latency_s": self.first_token_latency_s,
            "framework": self.framework,
            "model_id": self.model_id,
            "quant": self.quant,
            "prompt_token_count": self.prompt_token_count,
            "tokens_per_sec": self.tokens_per_sec,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> InferenceResult:
        """Deserialize from a plain dictionary (e.g. loaded from JSON)."""
        return cls(
            output_text=d["output_text"],
            tokens_generated=d["tokens_generated"],
            total_time_s=d["total_time_s"],
            first_token_latency_s=d["first_token_latency_s"],
            framework=d["framework"],
            model_id=d["model_id"],
            quant=d["quant"],
            prompt_token_count=d.get("prompt_token_count", 0),
            tokens_per_sec=d.get("tokens_per_sec", 0.0),
            metadata=d.get("metadata", {}),
        )


class RunnerProtocol(Protocol):
    """Structural interface every framework runner must satisfy.

    Using typing.Protocol (structural subtyping) means third-party wrappers
    satisfy this interface without inheriting from it.
    """

    def load(self, model_id: str, quant: QuantizationConfig) -> None:
        """Download (if needed) and prepare the model for inference."""
        ...

    def infer(self, prompt: str, max_tokens: int) -> InferenceResult:
        """Run inference and return timing + text results."""
        ...

    def unload(self) -> None:
        """Release model weights and free memory."""
        ...

    def health_check(self) -> bool:
        """Return True if the runner is ready to accept load() calls."""
        ...
