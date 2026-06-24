"""Config loader — reads setup.json and validates every field."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hw5.shared.constants import (
    ASSETS_DIR,
    DEFAULT_OLLAMA_HOST,
    RESULTS_DIR,
    SUPPORTED_QUANT_LEVELS,
    VALID_FRAMEWORKS,
)

log = logging.getLogger(__name__)

_REQUIRED = (
    "quantization_levels",
    "frameworks",
    "eval_prompt",
    "max_tokens",
    "monitor_interval_s",
    "vram_spike_threshold_mb",
)


class ConfigError(ValueError):
    """Raised when configuration is invalid or a required key is absent."""


@dataclass
class Config:
    """All evaluation pipeline settings, loaded from setup.json."""

    quantization_levels: list[str]
    frameworks: list[str]
    eval_prompt: str
    max_tokens: int
    monitor_interval_s: float
    vram_spike_threshold_mb: float
    ollama_host: str
    resume: bool
    results_dir: str
    assets_dir: str
    cpu_only_mode: bool = False

    @classmethod
    def load(cls, path: str) -> Config:
        """Load and validate config from a JSON file path."""
        try:
            raw = Path(path).read_text()
            data: dict[str, Any] = json.loads(raw)
        except FileNotFoundError as e:
            raise ConfigError(f"Config file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise ConfigError(f"Config file is not valid JSON: {path}") from e
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Config:
        """Build and validate a Config from a raw dict."""
        for key in _REQUIRED:
            if key not in data:
                raise ConfigError(f"Required config key missing: '{key}'")

        cfg = cls(
            quantization_levels=list(data["quantization_levels"]),
            frameworks=list(data["frameworks"]),
            eval_prompt=str(data["eval_prompt"]),
            max_tokens=int(data["max_tokens"]),
            monitor_interval_s=float(data["monitor_interval_s"]),
            vram_spike_threshold_mb=float(data["vram_spike_threshold_mb"]),
            ollama_host=str(data.get("ollama_host", DEFAULT_OLLAMA_HOST)),
            resume=bool(data.get("resume", False)),
            results_dir=str(data.get("results_dir", RESULTS_DIR)),
            assets_dir=str(data.get("assets_dir", ASSETS_DIR)),
            cpu_only_mode=bool(data.get("cpu_only_mode", False)),
        )
        _validate(cfg)
        return cfg

    def get(self, key: str, default: Any = None) -> Any:
        """Return attribute value by name, or default if the attribute is absent."""
        return getattr(self, key, default)

    def require(self, key: str) -> Any:
        """Return attribute value by name, raising ConfigError if it is None."""
        val = getattr(self, key, None)
        if val is None:
            raise ConfigError(f"Required config key missing: {key}")
        return val

    def to_dict(self) -> dict[str, Any]:
        """Serialize this config to a plain dictionary."""
        return asdict(self)


def _validate(cfg: Config) -> None:
    """Raise ConfigError for any invalid field value in cfg."""
    if cfg.monitor_interval_s <= 0:
        raise ConfigError("monitor_interval_s must be > 0")
    if cfg.vram_spike_threshold_mb <= 0:
        raise ConfigError("vram_spike_threshold_mb must be > 0")
    if cfg.max_tokens < 1:
        raise ConfigError("max_tokens must be a positive integer")
    if not cfg.quantization_levels:
        raise ConfigError("quantization_levels must be non-empty")
    invalid_q = set(cfg.quantization_levels) - set(SUPPORTED_QUANT_LEVELS)
    if invalid_q:
        raise ConfigError(f"Unsupported quantization levels: {sorted(invalid_q)}")
    if not cfg.frameworks:
        raise ConfigError("frameworks must be non-empty")
    invalid_fw = set(cfg.frameworks) - set(VALID_FRAMEWORKS)
    if invalid_fw:
        raise ConfigError(f"Unknown frameworks: {sorted(invalid_fw)}")
    if not Path(cfg.results_dir).exists():
        log.warning("results_dir does not exist yet: %s", cfg.results_dir)
