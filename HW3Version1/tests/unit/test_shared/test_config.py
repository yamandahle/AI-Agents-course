"""Unit tests for shared/config.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from article_writer.shared.config import load_config, load_rate_limits


def _write_config(tmp_path: Path) -> Path:
    cfg = {
        "version": "1.00",
        "llm": {"provider": "anthropic", "model": "claude-sonnet-4-6", "temperature": 0.3},
        "research": {
            "search_backend": "gemini", "fallback_backend": "perplexity",
            "batch_size": 5, "max_batches": 10, "min_confidence": "MEDIUM"
        },
        "writing": {"max_evaluator_iterations": 3, "score_threshold": 8.0, "target_pages": 15},
        "latex": {"compiler": "lualatex", "compile_passes": 4},
    }
    p = tmp_path / "setup.json"
    p.write_text(json.dumps(cfg))
    return p


def _write_rate_limits(tmp_path: Path) -> Path:
    rl = {"rate_limits": {"version": "1.00", "services": {
        "default": {"requests_per_minute": 30, "requests_per_hour": 500, "concurrent_max": 3, "retry_after_seconds": 30, "max_retries": 3}
    }}}
    p = tmp_path / "rate_limits.json"
    p.write_text(json.dumps(rl))
    return p


def test_load_config_returns_correct_types(tmp_path: Path) -> None:
    p = _write_config(tmp_path)
    load_config.cache_clear()
    cfg = load_config(str(p))
    assert cfg.version == "1.00"
    assert cfg.llm.temperature == 0.3
    assert cfg.research.batch_size == 5
    assert cfg.writing.target_pages == 15
    assert cfg.latex.compile_passes == 4


def test_load_config_cached(tmp_path: Path) -> None:
    p = _write_config(tmp_path)
    load_config.cache_clear()
    cfg1 = load_config(str(p))
    cfg2 = load_config(str(p))
    assert cfg1 is cfg2


def test_load_config_raises_on_missing_file() -> None:
    load_config.cache_clear()
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/setup.json")


def test_load_rate_limits_returns_services(tmp_path: Path) -> None:
    p = _write_rate_limits(tmp_path)
    load_rate_limits.cache_clear()
    rl = load_rate_limits(str(p))
    assert "default" in rl
    assert "requests_per_minute" in rl["default"]
