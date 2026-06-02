"""Shared helpers for ApiGatekeeper unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate.shared.gatekeeper import ApiGatekeeper

CONFIG: dict = {
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


def make_mock_response(input_tokens: int = 10, output_tokens: int = 20) -> MagicMock:
    resp = MagicMock()
    resp.usage.input_tokens = input_tokens
    resp.usage.output_tokens = output_tokens
    resp.content = [MagicMock(text="Hello")]
    return resp


def make_gatekeeper(client: MagicMock | None = None) -> ApiGatekeeper:
    if client is None:
        client = MagicMock()
        client.messages.create.return_value = make_mock_response()
    return ApiGatekeeper(config=CONFIG, client=client)
