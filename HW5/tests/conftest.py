"""Shared pytest fixtures for unit and integration tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw5.shared.config import Config
from hw5.shared.quant_config import QuantizationConfig


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    """Write a minimal valid setup.json to a temp dir and return its path."""
    data = {
        "quantization_levels": ["Q4", "Q8", "Q2"],
        "frameworks": ["ollama", "airllm"],
        "eval_prompt": "Test prompt.",
        "max_tokens": 50,
        "monitor_interval_s": 0.5,
        "vram_spike_threshold_mb": 500,
        "ollama_host": "http://localhost:11434",
        "resume": False,
        "results_dir": str(tmp_path / "results"),
        "assets_dir": str(tmp_path / "assets"),
        "cpu_only_mode": True,
    }
    cfg_file = tmp_path / "setup.json"
    cfg_file.write_text(json.dumps(data))
    return cfg_file


@pytest.fixture
def config(config_path: Path) -> Config:
    """Return a Config loaded from the temp setup.json."""
    return Config.load(str(config_path))


@pytest.fixture
def quant_q4() -> QuantizationConfig:
    return QuantizationConfig.from_label("Q4")


@pytest.fixture
def quant_q8() -> QuantizationConfig:
    return QuantizationConfig.from_label("Q8")


@pytest.fixture
def quant_q2() -> QuantizationConfig:
    return QuantizationConfig.from_label("Q2")


@pytest.fixture
def models_json(tmp_path: Path) -> Path:
    """Write a minimal valid models.json to a temp dir and return its path."""
    data = {
        "models": [
            {
                "name": "model_a",
                "hf_repo_id": "test-org/model-a-7b",
                "ollama_tag": "model-a:7b",
                "local_cache": str(tmp_path / "cache"),
                "size_class": "large",
                "param_count_b": 7.0,
                "ollama_compatible": True,
                "airllm_compatible": True,
                "description": "Test large model",
                "quant_ollama_tags": {
                    "Q2": "model-a:7b-q2_K",
                    "Q4": "model-a:7b-q4_K_M",
                    "Q8": "model-a:7b-q8_0",
                },
                "quant_airllm_params": {
                    "Q2": "2bit",
                    "Q4": "4bit",
                    "Q8": "8bit",
                },
            },
            {
                "name": "model_b",
                "hf_repo_id": "test-org/model-b-1b",
                "ollama_tag": "model-b:1b",
                "local_cache": str(tmp_path / "cache"),
                "size_class": "small",
                "param_count_b": 1.5,
                "ollama_compatible": True,
                "airllm_compatible": True,
                "description": "Test small model",
                "quant_ollama_tags": {
                    "Q2": "model-b:1b-q2_K",
                    "Q4": "model-b:1b-q4_K_M",
                    "Q8": "model-b:1b-q8_0",
                },
                "quant_airllm_params": {
                    "Q2": "2bit",
                    "Q4": "4bit",
                    "Q8": "8bit",
                },
            },
        ]
    }
    path = tmp_path / "models.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def mock_gatekeeper() -> MagicMock:
    """Gatekeeper that immediately calls the wrapped function."""
    gk = MagicMock()
    gk.execute.side_effect = lambda fn, *a, **kw: fn(*a, **kw)
    return gk
