from __future__ import annotations

import json

import pytest

from hw4.shared.config import ConfigManager


def test_config_loads_agents_and_paths() -> None:
    config = ConfigManager("config")
    assert config.get("agents", "hub_degree_threshold") == 10
    assert "artifacts" in config.get("paths")


def test_rate_limit_openai() -> None:
    config = ConfigManager("config")
    limits = config.get_rate_limit("openai")
    assert limits["requests_per_minute"] == 30


def test_rate_limit_gemini() -> None:
    config = ConfigManager("config")
    limits = config.get_rate_limit("gemini")
    assert limits["requests_per_minute"] == 15


def test_rate_limit_anthropic() -> None:
    config = ConfigManager("config")
    limits = config.get_rate_limit("anthropic")
    assert limits["requests_per_minute"] == 50


def test_rate_limit_unknown_returns_empty_dict() -> None:
    config = ConfigManager("config")
    limits = config.get_rate_limit("unknown_provider")
    assert isinstance(limits, dict)


def test_version_mismatch_raises(tmp_path) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "setup.json").write_text(
        json.dumps({"version": "0.00", "agents": {}, "paths": {}})
    )
    (cfg_dir / "rate_limits.json").write_text(json.dumps({"services": {}}))
    with pytest.raises(RuntimeError, match="version mismatch"):
        ConfigManager(str(cfg_dir))
