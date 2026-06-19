from __future__ import annotations

from hw4.shared.config import ConfigManager


def test_config_loads_agents_and_paths() -> None:
    config = ConfigManager("config")
    assert config.get("agents", "hub_degree_threshold") == 10
    assert "artifacts" in config.get("paths")
