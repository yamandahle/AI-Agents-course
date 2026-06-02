"""ConfigManager — loads all configuration files from disk into typed properties."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from debate.shared.version import VERSION


class ConfigVersionError(ValueError):
    """Raised when a config file version does not match the application version."""


class ConfigManager:
    """Reads setup, rate_limits, and logging config from a directory of JSON files."""

    def __init__(self, config_dir: str = "config") -> None:
        base = Path(config_dir)
        self.setup = self._load_versioned(base / "setup.json")
        self.rate_limits = self._load_versioned(base / "rate_limits.json")
        self.logging_config = self._load_versioned(base / "logging_config.json")

    @staticmethod
    def _load_versioned(path: Path) -> dict[str, Any]:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        file_version = data.get("version")
        if file_version is not None and file_version != VERSION:
            raise ConfigVersionError(
                f"{path.name}: expected version {VERSION}, found {file_version!r}"
            )
        return data
