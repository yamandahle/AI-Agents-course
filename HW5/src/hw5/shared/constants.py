"""Pipeline-wide constants. Import from here, never hard-code values elsewhere."""

from __future__ import annotations

SAMPLE_INTERVAL_S: float = 0.5
VRAM_SPIKE_THRESHOLD_MB: float = 500.0
DEFAULT_MAX_TOKENS: int = 200
DEFAULT_OLLAMA_HOST: str = "http://localhost:11434"

SUPPORTED_QUANT_LEVELS: list[str] = ["Q2", "Q4", "Q8"]
VALID_FRAMEWORKS: list[str] = ["ollama", "airllm"]

FRAMEWORK_COLORS: dict[str, str] = {
    "ollama": "steelblue",
    "airllm": "darkorange",
}

QUANT_MARKERS: dict[str, str] = {
    "Q2": "^",
    "Q4": "o",
    "Q8": "s",
}

QUANT_LINESTYLES: dict[str, str] = {
    "Q2": "dotted",
    "Q4": "solid",
    "Q8": "dashed",
}

RESULTS_DIR: str = "results"
ASSETS_DIR: str = "assets"
