"""QuantizationConfig — maps Q2/Q4/Q8 labels to framework-specific strings."""

from __future__ import annotations

from dataclasses import dataclass

from hw5.shared.constants import SUPPORTED_QUANT_LEVELS

_LABEL_TO_BITS: dict[str, int] = {"Q2": 2, "Q4": 4, "Q8": 8}

_OLLAMA_TAGS: dict[str, str] = {
    "Q2": "q2_K",
    "Q4": "q4_K_M",
    "Q8": "q8_0",
}

_AIRLLM_PARAMS: dict[str, str] = {
    "Q2": "2bit",
    "Q4": "4bit",
    "Q8": "8bit",
}


@dataclass(frozen=True)
class QuantizationConfig:
    """Immutable quantization descriptor used by both Ollama and AirLLM runners."""

    bits: int
    label: str

    @classmethod
    def from_label(cls, label: str) -> QuantizationConfig:
        """Build a QuantizationConfig from a label string like 'Q4'."""
        upper = label.upper()
        if upper not in _LABEL_TO_BITS:
            raise ValueError(
                f"Unknown quantization label '{label}'. "
                f"Supported: {SUPPORTED_QUANT_LEVELS}"
            )
        return cls(bits=_LABEL_TO_BITS[upper], label=upper)

    def validate(self) -> None:
        """Raise ValueError if bits is not a supported quantization width."""
        if self.bits not in (2, 4, 8):
            raise ValueError(
                f"Unsupported quantization bits: {self.bits}. Must be 2, 4, or 8."
            )

    def to_ollama_tag(self) -> str:
        """Return the GGUF quantization suffix used by Ollama (e.g. 'q4_K_M')."""
        return _OLLAMA_TAGS[self.label]

    def to_airllm_param(self) -> str:
        """Return the compression string used by AirLLM (e.g. '4bit')."""
        return _AIRLLM_PARAMS[self.label]

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"QuantizationConfig(bits={self.bits}, label='{self.label}')"
