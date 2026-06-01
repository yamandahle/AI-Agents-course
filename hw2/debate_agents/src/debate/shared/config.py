"""ConfigManager — loads all configuration files from disk into typed properties."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Reads setup, rate_limits, and logging config from a directory of JSON files."""

    def __init__(self, config_dir: str = "config") -> None:
        base = Path(config_dir)
        self.setup: dict[str, Any] = json.loads((base / "setup.json").read_text(encoding="utf-8"))
        self.rate_limits: dict[str, Any] = json.loads(
            (base / "rate_limits.json").read_text(encoding="utf-8")
        )
        self.logging_config: dict[str, Any] = json.loads(
            (base / "logging_config.json").read_text(encoding="utf-8")
        )
