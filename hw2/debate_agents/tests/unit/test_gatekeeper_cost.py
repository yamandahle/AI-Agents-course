"""Tests for ApiGatekeeper token counting, budget enforcement, logging, and bypass prevention."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from gatekeeper_test_helpers import CONFIG, MODEL, make_gatekeeper, make_mock_response

from debate.shared.gatekeeper import ApiGatekeeper, BudgetExceededError


class TestTokenCounting:
    def test_input_and_output_tokens_counted_separately(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response(input_tokens=50, output_tokens=80)
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=100)

        table = gk.get_cost_table()
        assert len(table) == 1
        assert table[0]["input_tokens"] == 50
        assert table[0]["output_tokens"] == 80

    def test_cost_calculated_correctly(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response(
            input_tokens=1_000_000, output_tokens=1_000_000
        )
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            with pytest.raises(BudgetExceededError):
                gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=100)

        entry = gk.get_cost_table()[0]
        assert abs(entry["cost_usd"] - 4.80) < 1e-6


class TestBudgetAlert:
    def test_raises_budget_exceeded_when_over_limit(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response(
            input_tokens=1_000_000, output_tokens=1_000_000
        )
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            with pytest.raises(BudgetExceededError):
                gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=100)

    def test_no_error_when_under_budget(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response(input_tokens=10, output_tokens=20)
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=50)


class TestLogging:
    def test_every_call_logged(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 1_000_000.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "a"}], max_tokens=10)
            gk.call(model=MODEL, messages=[{"role": "user", "content": "b"}], max_tokens=10)

        assert len(gk.get_cost_table()) == 2

    def test_log_entry_has_required_fields(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
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
        gk = make_gatekeeper()

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=10)

        table = gk.get_cost_table()
        table.clear()
        assert len(gk.get_cost_table()) == 1


class TestNoBypassing:
    def test_client_always_called_through_gatekeeper(self) -> None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
        gk = ApiGatekeeper(config=CONFIG, client=client)
        messages = [{"role": "user", "content": "test"}]

        with patch("debate.shared.gatekeeper.time") as mock_time:
            mock_time.time.return_value = 0.0
            mock_time.sleep = MagicMock()
            gk.call(model=MODEL, messages=messages, max_tokens=50)

        client.messages.create.assert_called_once_with(model=MODEL, messages=messages, max_tokens=50)
