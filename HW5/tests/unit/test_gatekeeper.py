"""T092–T095: Tests for ApiGatekeeper token-bucket rate limiter."""

from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from hw5.shared.gatekeeper import ApiGatekeeper


# T092 — rate limiting causes a sleep when bucket is empty
def test_rate_limiting_sleeps_when_bucket_depleted():
    gk = ApiGatekeeper(rate=1.0, burst=1)
    # Drain the single token so next call must wait.
    gk._tokens = 0.0
    fixed = time.monotonic()
    gk._last_refill = fixed

    with (
        patch("hw5.shared.gatekeeper.time.sleep") as mock_sleep,
        patch("hw5.shared.gatekeeper.time.monotonic", return_value=fixed),
    ):
        gk.execute(lambda: None)

    mock_sleep.assert_called_once()
    wait_arg = mock_sleep.call_args[0][0]
    assert wait_arg == pytest.approx(1.0, rel=0.05)


def test_execute_calls_function_and_returns_result():
    gk = ApiGatekeeper(rate=1000.0, burst=100)
    result = gk.execute(lambda x: x * 2, 21)
    assert result == 42


def test_execute_passes_kwargs():
    gk = ApiGatekeeper(rate=1000.0, burst=100)

    def fn(a, b=0):
        return a + b

    assert gk.execute(fn, 3, b=7) == 10


# T093 — concurrent calls all succeed without data corruption
def test_concurrent_calls_all_complete():
    gk = ApiGatekeeper(rate=1000.0, burst=50)
    results: list[int] = []
    lock = threading.Lock()

    def task(n: int) -> None:
        gk.execute(lambda: None)
        with lock:
            results.append(n)

    threads = [threading.Thread(target=task, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)

    assert len(results) == 20
    assert sorted(results) == list(range(20))


def test_context_manager_does_not_raise():
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    with gk:
        pass  # must not raise


# T094 — set_rate changes the rate attribute
def test_set_rate_updates_internal_rate():
    gk = ApiGatekeeper(rate=5.0, burst=10)
    gk.set_rate(2.0)
    assert gk._rate == pytest.approx(2.0)


def test_set_rate_zero_raises():
    gk = ApiGatekeeper(rate=5.0, burst=10)
    with pytest.raises(ValueError, match="rate must be > 0"):
        gk.set_rate(0.0)


def test_set_rate_negative_raises():
    gk = ApiGatekeeper(rate=5.0, burst=10)
    with pytest.raises(ValueError, match="rate must be > 0"):
        gk.set_rate(-1.0)


def test_init_zero_rate_raises():
    with pytest.raises(ValueError, match="rate must be > 0"):
        ApiGatekeeper(rate=0.0)


# T095 — reset() refills token bucket
def test_reset_refills_tokens_to_burst():
    gk = ApiGatekeeper(rate=1.0, burst=5)
    gk._tokens = 0.0
    gk.reset()
    assert gk._tokens == pytest.approx(5.0)


def test_after_reset_execute_does_not_sleep():
    gk = ApiGatekeeper(rate=1.0, burst=1)
    gk._tokens = 0.0
    gk.reset()  # refills to 1 token

    with patch("hw5.shared.gatekeeper.time.sleep") as mock_sleep:
        gk.execute(lambda: None)

    mock_sleep.assert_not_called()


def test_from_config_loads_rate(tmp_path):
    import json

    cfg = tmp_path / "rate_limits.json"
    cfg.write_text(json.dumps({"huggingface_download_rps": 3}))
    gk = ApiGatekeeper.from_config(str(cfg))
    assert gk._rate == pytest.approx(3.0)
