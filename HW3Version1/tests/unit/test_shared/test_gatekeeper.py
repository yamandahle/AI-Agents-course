"""Unit tests for shared/gatekeeper.py."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from article_writer.shared.config import load_rate_limits
from article_writer.shared.gatekeeper import ApiGatekeeper


def _setup_rate_limits(tmp_path: Path, rpm: int = 30) -> None:
    rl = {"rate_limits": {"version": "1.00", "services": {
        "default": {"requests_per_minute": rpm, "requests_per_hour": 1000, "concurrent_max": 5, "retry_after_seconds": 0, "max_retries": 3},
        "test_svc": {"requests_per_minute": rpm, "requests_per_hour": 1000, "concurrent_max": 5, "retry_after_seconds": 0, "max_retries": 2},
    }}}
    p = tmp_path / "config"
    p.mkdir(exist_ok=True)
    (p / "rate_limits.json").write_text(json.dumps(rl))


def test_execute_calls_api_call(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _setup_rate_limits(tmp_path)
    load_rate_limits.cache_clear()
    gate = ApiGatekeeper()
    mock_fn = MagicMock(return_value="result")
    result = gate.execute("test_svc", mock_fn)
    assert result == "result"
    mock_fn.assert_called_once()


def test_execute_retries_on_exception(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _setup_rate_limits(tmp_path)
    load_rate_limits.cache_clear()
    gate = ApiGatekeeper()
    call_count = 0

    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("transient")
        return "ok"

    result = gate.execute("test_svc", flaky)
    assert result == "ok"
    assert call_count == 2


def test_execute_raises_after_max_retries(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _setup_rate_limits(tmp_path)
    load_rate_limits.cache_clear()
    gate = ApiGatekeeper()
    with pytest.raises(RuntimeError, match="All retries exhausted"):
        gate.execute("test_svc", lambda: (_ for _ in ()).throw(RuntimeError("always fails")))


def test_get_queue_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _setup_rate_limits(tmp_path)
    load_rate_limits.cache_clear()
    gate = ApiGatekeeper()
    status = gate.get_queue_status()
    assert status.active_calls == 0
