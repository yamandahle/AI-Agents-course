"""Unit tests for ApiGatekeeper — TDD Red phase written before implementation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from debate.shared.gatekeeper import ApiGatekeeper, BudgetExceededError

# ---------------------------------------------------------------------------
# Minimal config for fast tests — no real API calls, tiny budget
# ---------------------------------------------------------------------------
CONFIG = {
    "version": "1.00",
    "anthropic": {
        "requests_per_minute": 2,
        "max_tokens_per_call": 1000,
        "daily_budget_usd": 0.001,
        "retry_attempts": 3,
        "retry_backoff_seconds": [0.001, 0.001, 0.001],
        "model_costs": {
            "claude-haiku-4-5": {
                "input_per_million": 0.80,
                "output_per_million": 4.00,
            },
        },
    },
    "tavily": {"requests_per_minute": 5, "max_results_per_search": 3},
}

MODEL = "claude-haiku-4-5"


def _make_mock_response(input_tokens: int = 10, output_tokens: int = 20) -> MagicMock:
    """Return a fake Anthropic response object."""
    resp = MagicMock()
    resp.usage.input_tokens = input_tokens
    resp.usage.output_tokens = output_tokens
    resp.content = [MagicMock(text="Hello")]
    return resp


def _make_gatekeeper(client: MagicMock | None = None) -> ApiGatekeeper:
    if client is None:
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
    return ApiGatekeeper(config=CONFIG, client=client)


# ---------------------------------------------------------------------------
# 1. Rate limiting blocks when limit is hit
# ---------------------------------------------------------------------------
class TestRateLimiting:
    def test_blocks_when_limit_reached(self) -> None:
        """Third call within one minute must trigger a sleep (rate limit enforced)."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)
            # Third call — window is full, sleep must be called
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

            mock_time.sleep.assert_called()

    def test_does_not_block_below_limit(self) -> None:
        """Calls within the rate limit must NOT trigger sleep."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

            mock_time.sleep.assert_not_called()


# ---------------------------------------------------------------------------
# 2. FIFO queue fills correctly
# ---------------------------------------------------------------------------
class TestFifoQueue:
    def test_queue_holds_timestamps_in_order(self) -> None:
        """Each successful call must push a timestamp into the internal FIFO deque."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            # Each call() hits time.time() 3×: enforce-start, enforce-append, record-timestamp
            mock_time.time.side_effect = [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "a"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "b"}], max_tokens=10)

        assert len(gk._request_times) == 2  # noqa: SLF001
        timestamps = list(gk._request_times)  # noqa: SLF001
        assert timestamps[0] <= timestamps[1], "FIFO order must be preserved"


# ---------------------------------------------------------------------------
# 3. Retry with exponential backoff
# ---------------------------------------------------------------------------
class TestRetryBackoff:
    def test_retries_on_failure_then_succeeds(self) -> None:
        """Gatekeeper must retry up to retry_attempts times on API error."""
        client = MagicMock()
        client.messages.create.side_effect = [
            Exception("transient error"),
            Exception("transient error"),
            _make_mock_response(),
        ]
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            result = gk.call(
                model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10
            )

        assert result is not None
        assert client.messages.create.call_count == 3

    def test_raises_after_all_retries_exhausted(self) -> None:
        """After retry_attempts failures Gatekeeper must re-raise the last exception."""
        client = MagicMock()
        client.messages.create.side_effect = Exception("persistent error")
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            with pytest.raises(Exception, match="persistent error"):
                gk.call(
                    model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10
                )

        assert client.messages.create.call_count == CONFIG["anthropic"]["retry_attempts"]

    def test_backoff_sleeps_between_retries(self) -> None:
        """Sleep must be called with the configured backoff values between retries."""
        client = MagicMock()
        client.messages.create.side_effect = [
            Exception("err"),
            Exception("err"),
            _make_mock_response(),
        ]
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        # Two failures → two backoff sleeps (index 0 and 1)
        backoff_calls = [
            call.args[0]
            for call in mock_time.sleep.call_args_list
            if call.args[0] in CONFIG["anthropic"]["retry_backoff_seconds"]
        ]
        assert len(backoff_calls) == 2


# ---------------------------------------------------------------------------
# 4. Token counting — input and output tracked separately
# ---------------------------------------------------------------------------
class TestTokenCounting:
    def test_input_and_output_tokens_counted_separately(self) -> None:
        """Cost table entry must record input_tokens and output_tokens independently."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response(input_tokens=50, output_tokens=80)
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=100)

        table = gk.get_cost_table()
        assert len(table) == 1
        entry = table[0]
        assert entry["input_tokens"] == 50
        assert entry["output_tokens"] == 80

    def test_cost_calculated_correctly(self) -> None:
        """Cost must use per-million pricing from config, not hardcoded values."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response(
            input_tokens=1_000_000, output_tokens=1_000_000
        )
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            with pytest.raises(BudgetExceededError):
                gk.call(
                    model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=100
                )

        # Even though budget exceeded, the entry must be logged
        table = gk.get_cost_table()
        assert len(table) == 1
        entry = table[0]
        # 1M input @ $0.80 + 1M output @ $4.00 = $4.80
        assert abs(entry["cost_usd"] - 4.80) < 1e-6


# ---------------------------------------------------------------------------
# 5. Budget alert triggers at threshold
# ---------------------------------------------------------------------------
class TestBudgetAlert:
    def test_raises_budget_exceeded_when_over_limit(self) -> None:
        """Call that pushes cumulative cost past daily_budget_usd must raise BudgetExceededError."""
        client = MagicMock()
        # 1M tokens each → cost >> $0.001 budget
        client.messages.create.return_value = _make_mock_response(
            input_tokens=1_000_000, output_tokens=1_000_000
        )
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            with pytest.raises(BudgetExceededError):
                gk.call(
                    model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=100
                )

    def test_no_error_when_under_budget(self) -> None:
        """Normal-sized calls well under budget must not raise."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response(input_tokens=10, output_tokens=20)
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=50)
        # No exception means the test passes


# ---------------------------------------------------------------------------
# 6. Every API call logged with timestamp
# ---------------------------------------------------------------------------
class TestLogging:
    def test_every_call_logged(self) -> None:
        """get_cost_table() must return one entry per successful API call."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 1_000_000.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "a"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "b"}], max_tokens=10)

        table = gk.get_cost_table()
        assert len(table) == 2

    def test_log_entry_has_required_fields(self) -> None:
        """Each cost-table entry must include all required fields."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 42.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        entry = gk.get_cost_table()[0]
        required = {"timestamp", "model", "input_tokens", "output_tokens", "cost_usd", "cumulative_cost_usd"}
        assert required.issubset(entry.keys())
        assert entry["timestamp"] == 42.0
        assert entry["model"] == MODEL

    def test_get_cost_table_returns_copy(self) -> None:
        """Mutating the returned list must not affect internal state."""
        gk = _make_gatekeeper()

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        table = gk.get_cost_table()
        table.clear()
        assert len(gk.get_cost_table()) == 1, "Internal log must not be affected by external mutation"


# ---------------------------------------------------------------------------
# 7. No direct API calls bypass the gatekeeper
# ---------------------------------------------------------------------------
class TestNoBypassing:
    def test_client_always_called_through_gatekeeper(self) -> None:
        """Client.messages.create must be called with the exact args passed to call()."""
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        messages = [{"role": "user", "content": "test"}]

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()

            gk.call(model=MODEL, messages=messages, max_tokens=50)

        client.messages.create.assert_called_once_with(
            model=MODEL, messages=messages, max_tokens=50
        )
