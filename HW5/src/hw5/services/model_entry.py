"""ModelEntry dataclass — one record in the model registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

_VALID_SIZE_CLASSES = ("small", "large")


@dataclass
class ModelEntry:
    """Describes a single model available to the evaluation pipeline."""

    name: str
    hf_repo_id: str
    ollama_tag: str
    local_cache: str
    size_class: str
    ollama_compatible: bool
    airllm_compatible: bool
    description: str
    param_count_b: float = 0.0
    quant_ollama_tags: dict[str, str] = field(default_factory=dict)
    quant_airllm_params: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.size_class not in _VALID_SIZE_CLASSES:
            raise ValueError(
                f"Invalid size_class '{self.size_class}' for model '{self.name}'. "
                f"Must be one of: {_VALID_SIZE_CLASSES}"
            )

    def __str__(self) -> str:
        return f"{self.name} ({self.size_class})"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain JSON-compatible dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ModelEntry:
        """Deserialize from a plain dictionary (e.g. one entry in models.json)."""
        return cls(
            name=str(d["name"]),
            hf_repo_id=str(d["hf_repo_id"]),
            ollama_tag=str(d.get("ollama_tag", "")),
            local_cache=str(d["local_cache"]),
            size_class=str(d["size_class"]),
            ollama_compatible=bool(d.get("ollama_compatible", True)),
            airllm_compatible=bool(d.get("airllm_compatible", True)),
            description=str(d.get("description", "")),
            param_count_b=float(d.get("param_count_b", 0.0)),
            quant_ollama_tags=dict(d.get("quant_ollama_tags", {})),
            quant_airllm_params=dict(d.get("quant_airllm_params", {})),
        )

    def ollama_tag_for(self, quant_label: str) -> str:
        """Return the Ollama pull tag for a given quantization label."""
        return self.quant_ollama_tags.get(
            quant_label, f"{self.ollama_tag}-{quant_label.lower()}"
        )

    def airllm_param_for(self, quant_label: str) -> str:
        """Return the AirLLM compression string for a given quantization label."""
        return self.quant_airllm_params.get(quant_label, f"{int(quant_label[1:])}bit")
