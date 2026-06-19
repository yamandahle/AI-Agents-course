"""Unit tests for shared/gatekeeper.py — covers execute, retry, and rate limiting."""
from __future__ import annotations

import time

import pytest

from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig


def _gk(**overrides) -> ApiGatekeeper:
    defaults = {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "concurrent_max": 5,
        "retry_after_seconds": 0,
        "max_retries": 3,
    }
    defaults.update(overrides)
    return ApiGatekeeper(config=RateLimitConfig(**defaults))


# ── execute — happy path ──────────────────────────────────────────────────────

def test_execute_calls_function_and_returns_result() -> None:
    gk = _gk()
    assert gk.execute(lambda: "hello") == "hello"


def test_execute_passes_args_and_kwargs() -> None:
    gk = _gk()
    result = gk.execute(lambda x, y=0: x + y, 3, y=4)
    assert result == 7


# ── execute — retry logic ─────────────────────────────────────────────────────

def test_execute_retries_on_exception_then_succeeds() -> None:
    gk = _gk(max_retries=3, retry_after_seconds=0)
    calls = [0]

    def flaky():
        calls[0] += 1
        if calls[0] < 3:
            raise RuntimeError("transient")
        return "ok"

    assert gk.execute(flaky) == "ok"
    assert calls[0] == 3


def test_execute_raises_after_max_retries_exhausted() -> None:
    gk = _gk(max_retries=2, retry_after_seconds=0)

    with pytest.raises(RuntimeError, match="always"):
        gk.execute(lambda: (_ for _ in ()).throw(RuntimeError("always")))


def test_execute_records_call_on_success() -> None:
    gk = _gk()
    assert len(gk._call_times) == 0
    gk.execute(lambda: None)
    assert len(gk._call_times) == 1


# ── _record_call ──────────────────────────────────────────────────────────────

def test_record_call_appends_timestamp() -> None:
    gk = _gk()
    before = time.time()
    gk._record_call()
    after = time.time()
    assert len(gk._call_times) == 1
    assert before <= gk._call_times[0] <= after


def test_record_call_multiple_times() -> None:
    gk = _gk()
    gk._record_call()
    gk._record_call()
    gk._record_call()
    assert len(gk._call_times) == 3


# ── _wait_if_rate_limited ─────────────────────────────────────────────────────

def test_wait_if_rate_limited_does_not_sleep_when_under_limit(monkeypatch) -> None:
    gk = _gk(requests_per_minute=5)
    slept = []
    monkeypatch.setattr("hw4.shared.gatekeeper.time.sleep", lambda s: slept.append(s))
    gk._wait_if_rate_limited()
    assert slept == []


def test_wait_if_rate_limited_sleeps_when_at_limit(monkeypatch) -> None:
    gk = _gk(requests_per_minute=1)
    slept = []
    monkeypatch.setattr("hw4.shared.gatekeeper.time.sleep", lambda s: slept.append(s))
    # Fill the call_times bucket to the limit
    gk._call_times = [time.time()]
    gk._wait_if_rate_limited()
    assert len(slept) == 1
    assert slept[0] >= 0


def test_wait_if_rate_limited_prunes_old_timestamps(monkeypatch) -> None:
    gk = _gk(requests_per_minute=2)
    slept = []
    monkeypatch.setattr("hw4.shared.gatekeeper.time.sleep", lambda s: slept.append(s))
    # Two calls that happened 61 seconds ago (outside the 60s window)
    old = time.time() - 61
    gk._call_times = [old, old]
    gk._wait_if_rate_limited()
    assert slept == []  # old calls pruned; under limit again
