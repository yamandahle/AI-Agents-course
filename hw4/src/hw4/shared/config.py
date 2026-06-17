from __future__ import annotations

import json
from pathlib import Path


class ConfigManager:
    def __init__(self, config_dir: str = "config") -> None:
        self._dir = Path(config_dir)
        self._setup = self._load("setup.json")
        self._rate_limits = self._load("rate_limits.json")

    def _load(self, filename: str) -> dict:
        path = self._dir / filename
        with path.open() as f:
            return json.load(f)

    def get(self, *keys: str) -> any:
        data = self._setup
        for key in keys:
            data = data[key]
        return data

    def get_rate_limit(self, service: str) -> dict:
        services = self._rate_limits.get("services", {})
        return services.get(service, services.get("default", {}))
