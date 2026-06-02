"""Tests for ApiGatekeeper rate limiting, FIFO queue, and retry backoff."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from gatekeeper_test_helpers import CONFIG, MODEL, make_mock_response

from debate.shared.gatekeeper import ApiGatekeeper


class TestRateLimiting:
    def test_blocks_when_limit_reached(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)
            mock_time.sleep.assert_called()

    def test_does_not_block_below_limit(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)
            mock_time.sleep.assert_not_called()


class TestFifoQueue:
    def test_queue_holds_timestamps_in_order(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.side_effect = [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "a"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "b"}], max_tokens=10)

        assert len(gk._request_times) == 2  # noqa: SLF001
        timestamps = list(gk._request_times)  # noqa: SLF001
        assert timestamps[0] <= timestamps[1]


class TestRetryBackoff:
    def test_retries_on_failure_then_succeeds(self) -> None:
        client = MagicMock()
        client.messages.create.side_effect = [
            Exception("transient error"), Exception("transient error"), make_mock_response(),
        ]
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            result = gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        assert result is not None
        assert client.messages.create.call_count == 3

    def test_raises_after_all_retries_exhausted(self) -> None:
        client = MagicMock()
        client.messages.create.side_effect = Exception("persistent error")
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            with pytest.raises(Exception, match="persistent error"):
                gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        assert client.messages.create.call_count == CONFIG["anthropic"]["retry_attempts"]

    def test_backoff_sleeps_between_retries(self) -> None:
        client = MagicMock()
        client.messages.create.side_effect = [Exception("err"), Exception("err"), make_mock_response()]
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        backoff_calls = [
            call.args[0]
            for call in mock_time.sleep.call_args_list
            if call.args[0] in CONFIG["anthropic"]["retry_backoff_seconds"]
        ]
        assert len(backoff_calls) == 2
