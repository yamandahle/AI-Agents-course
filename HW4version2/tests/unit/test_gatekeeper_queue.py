"""Unit tests for ApiGatekeeper queue management — get_queue_status and overflow."""
from __future__ import annotations

import contextlib
import threading
import time

import pytest

from hw4.shared.gatekeeper import ApiGatekeeper, QueueStatus, RateLimitConfig


def _gk(**overrides) -> ApiGatekeeper:
    defaults = {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "concurrent_max": 5,
        "retry_after_seconds": 0,
        "max_retries": 1,
        "queue_max_depth": 10,
    }
    defaults.update(overrides)
    return ApiGatekeeper(config=RateLimitConfig(**defaults))


# ── get_queue_status ──────────────────────────────────────────────────────────

def test_get_queue_status_returns_queue_status_type() -> None:
    gk = _gk()
    assert isinstance(gk.get_queue_status(), QueueStatus)


def test_get_queue_status_idle_has_zero_depth() -> None:
    gk = _gk(queue_max_depth=5)
    status = gk.get_queue_status()
    assert status.queue_depth == 0
    assert status.max_queue_depth == 5


def test_get_queue_status_reflects_config_limits() -> None:
    gk = _gk(requests_per_minute=30, queue_max_depth=50)
    status = gk.get_queue_status()
    assert status.limit_per_minute == 30
    assert status.max_queue_depth == 50


def test_get_queue_status_counts_calls_this_minute() -> None:
    gk = _gk()
    gk.execute(lambda: None)
    gk.execute(lambda: None)
    status = gk.get_queue_status()
    assert status.calls_this_minute == 2


def test_get_queue_status_depth_is_zero_after_call_completes() -> None:
    gk = _gk()
    gk.execute(lambda: None)
    assert gk.get_queue_status().queue_depth == 0


def test_get_queue_status_depth_nonzero_during_execution() -> None:
    gk = _gk(concurrent_max=1)
    depths: list[int] = []
    barrier = threading.Barrier(2)

    def slow_call() -> str:
        barrier.wait(timeout=2)
        time.sleep(0.05)
        return "ok"

    t = threading.Thread(target=lambda: gk.execute(slow_call))
    t.start()
    barrier.wait(timeout=2)
    depths.append(gk.get_queue_status().queue_depth)
    t.join(timeout=2)

    assert depths[0] >= 1


# ── queue overflow / backpressure ─────────────────────────────────────────────

def test_queue_overflow_raises_when_full() -> None:
    gk = _gk(queue_max_depth=0)
    with pytest.raises(RuntimeError, match="queue full"):
        gk.execute(lambda: None)


def test_queue_depth_zero_after_overflow_error() -> None:
    gk = _gk(queue_max_depth=0)
    with contextlib.suppress(RuntimeError):
        gk.execute(lambda: None)
    assert gk.get_queue_status().queue_depth == 0
