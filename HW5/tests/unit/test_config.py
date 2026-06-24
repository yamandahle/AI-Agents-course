"""T067–T070: Tests for Config loader and ConfigError."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hw5.shared.config import Config, ConfigError


def _write_cfg(tmp_path: Path, overrides: dict | None = None) -> str:
    """Write a valid setup.json and return its path string."""
    data = {
        "quantization_levels": ["Q4", "Q8"],
        "frameworks": ["ollama", "airllm"],
        "eval_prompt": "Test prompt.",
        "max_tokens": 100,
        "monitor_interval_s": 0.5,
        "vram_spike_threshold_mb": 500.0,
        "ollama_host": "http://localhost:11434",
        "resume": False,
        "results_dir": str(tmp_path / "results"),
        "assets_dir": str(tmp_path / "assets"),
        "cpu_only_mode": True,
    }
    if overrides:
        data.update(overrides)
    p = tmp_path / "setup.json"
    p.write_text(json.dumps(data))
    return str(p)


# T067 — happy path
def test_load_returns_config(tmp_path):
    path = _write_cfg(tmp_path)
    cfg = Config.load(path)
    assert isinstance(cfg, Config)
    assert cfg.max_tokens == 100
    assert cfg.frameworks == ["ollama", "airllm"]
    assert cfg.quantization_levels == ["Q4", "Q8"]
    assert cfg.monitor_interval_s == pytest.approx(0.5)
    assert cfg.cpu_only_mode is True


def test_to_dict_roundtrip(tmp_path):
    cfg = Config.load(_write_cfg(tmp_path))
    d = cfg.to_dict()
    assert d["max_tokens"] == 100
    assert d["frameworks"] == ["ollama", "airllm"]


# T068 — missing required key
@pytest.mark.parametrize(
    "missing_key",
    [
        "quantization_levels",
        "frameworks",
        "eval_prompt",
        "max_tokens",
        "monitor_interval_s",
        "vram_spike_threshold_mb",
    ],
)
def test_missing_required_key_raises_config_error(tmp_path, missing_key):
    data = {
        "quantization_levels": ["Q4"],
        "frameworks": ["ollama"],
        "eval_prompt": "p",
        "max_tokens": 10,
        "monitor_interval_s": 0.5,
        "vram_spike_threshold_mb": 100,
    }
    del data[missing_key]
    p = tmp_path / "setup.json"
    p.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match=missing_key):
        Config.load(str(p))


# T069 — invalid values
def test_invalid_monitor_interval_raises(tmp_path):
    with pytest.raises(ConfigError, match="monitor_interval_s"):
        Config.load(_write_cfg(tmp_path, {"monitor_interval_s": -1}))


def test_zero_monitor_interval_raises(tmp_path):
    with pytest.raises(ConfigError, match="monitor_interval_s"):
        Config.load(_write_cfg(tmp_path, {"monitor_interval_s": 0}))


def test_invalid_vram_threshold_raises(tmp_path):
    with pytest.raises(ConfigError, match="vram_spike_threshold_mb"):
        Config.load(_write_cfg(tmp_path, {"vram_spike_threshold_mb": 0}))


def test_zero_max_tokens_raises(tmp_path):
    with pytest.raises(ConfigError, match="max_tokens"):
        Config.load(_write_cfg(tmp_path, {"max_tokens": 0}))


def test_unsupported_quant_level_raises(tmp_path):
    with pytest.raises(ConfigError, match="Unsupported quantization"):
        Config.load(_write_cfg(tmp_path, {"quantization_levels": ["Q16"]}))


def test_unknown_framework_raises(tmp_path):
    with pytest.raises(ConfigError, match="Unknown frameworks"):
        Config.load(_write_cfg(tmp_path, {"frameworks": ["vllm"]}))


def test_file_not_found_raises_config_error(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        Config.load(str(tmp_path / "missing.json"))


def test_invalid_json_raises_config_error(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json {{{")
    with pytest.raises(ConfigError, match="not valid JSON"):
        Config.load(str(p))


# T070 — get() with default
def test_get_returns_value(tmp_path):
    cfg = Config.load(_write_cfg(tmp_path))
    assert cfg.get("max_tokens") == 100


def test_get_returns_default_for_absent_key(tmp_path):
    cfg = Config.load(_write_cfg(tmp_path))
    assert cfg.get("nonexistent_key", "fallback") == "fallback"


def test_get_returns_none_default_when_no_default_given(tmp_path):
    cfg = Config.load(_write_cfg(tmp_path))
    assert cfg.get("nonexistent_key") is None


def test_require_raises_for_none_valued_key(tmp_path):
    cfg = Config.load(_write_cfg(tmp_path))
    with pytest.raises(ConfigError, match="missing"):
        cfg.require("nonexistent_key")


def test_ollama_host_defaults_when_absent(tmp_path):
    data = {
        "quantization_levels": ["Q4"],
        "frameworks": ["ollama"],
        "eval_prompt": "p",
        "max_tokens": 10,
        "monitor_interval_s": 0.5,
        "vram_spike_threshold_mb": 100,
    }
    p = tmp_path / "s.json"
    p.write_text(json.dumps(data))
    cfg = Config.load(str(p))
    assert "localhost" in cfg.ollama_host
