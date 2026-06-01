"""ApiGatekeeper — single choke point for all external API calls.

Enforces rate limits, exponential-backoff retries, per-call token accounting,
cumulative cost tracking, and daily budget enforcement. No caller may bypass this
class to reach the Anthropic API directly.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any


class BudgetExceededError(Exception):
    """Raised when a completed call pushes cumulative cost past daily_budget_usd."""


class ApiGatekeeper:
    """Rate-limited, budget-aware proxy for the Anthropic messages API."""

    def __init__(self, config: dict[str, Any], client: Any, logger: Any = None) -> None:
        cfg = config["anthropic"]
        self._rpm: int = cfg["requests_per_minute"]
        self._max_tokens: int = cfg["max_tokens_per_call"]
        self._daily_budget: float = cfg["daily_budget_usd"]
        self._retry_attempts: int = cfg["retry_attempts"]
        self._retry_backoff: list[float] = cfg["retry_backoff_seconds"]
        self._model_costs: dict[str, dict[str, float]] = cfg["model_costs"]

        self._client = client
        self._logger = logger

        # FIFO sliding window: stores call timestamps within the current minute
        self._request_times: deque[float] = deque()

        self._cost_log: list[dict[str, Any]] = []
        self._cumulative_cost: float = 0.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def call(
        self, model: str, messages: list[dict[str, Any]], max_tokens: int, agent: str = "unknown",
    ) -> Any:
        """Execute one Anthropic API call through the gatekeeper.

        Enforces rate limit, retries with backoff, logs tokens + cost,
        and raises BudgetExceededError if the daily limit is crossed.
        """
        self._enforce_rate_limit()
        response = self._call_with_retry(model=model, messages=messages, max_tokens=max_tokens)
        self._record_call(model=model, response=response, agent=agent)
        return response

    def get_cost_table(self) -> list[dict[str, Any]]:
        """Return a copy of the call log so callers cannot mutate internal state."""
        return list(self._cost_log)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _enforce_rate_limit(self) -> None:
        """Block until sending another request satisfies the per-minute rate limit."""
        now = time.time()
        window = 60.0

        # Drop timestamps older than one minute
        while self._request_times and now - self._request_times[0] >= window:
            self._request_times.popleft()

        if len(self._request_times) >= self._rpm:
            # Sleep until the oldest timestamp falls out of the window
            sleep_for = window - (now - self._request_times[0])
            if sleep_for > 0:
                time.sleep(sleep_for)
            # Re-evict after sleeping
            now = time.time()
            while self._request_times and now - self._request_times[0] >= window:
                self._request_times.popleft()

        self._request_times.append(time.time())

    def _call_with_retry(
        self, model: str, messages: list[dict[str, Any]], max_tokens: int
    ) -> Any:
        """Call client.messages.create with exponential backoff on failure."""
        last_exc: Exception | None = None
        for attempt in range(self._retry_attempts):
            try:
                return self._client.messages.create(
                    model=model, messages=messages, max_tokens=max_tokens
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt < self._retry_attempts - 1:
                    backoff = self._retry_backoff[min(attempt, len(self._retry_backoff) - 1)]
                    time.sleep(backoff)
        raise last_exc  # type: ignore[misc]

    def _record_call(self, model: str, response: Any, agent: str = "unknown") -> None:
        """Log token counts and cost; raise BudgetExceededError if limit exceeded."""
        input_tokens: int = response.usage.input_tokens
        output_tokens: int = response.usage.output_tokens
        cost = self._calculate_cost(model=model, input_tokens=input_tokens, output_tokens=output_tokens)

        self._cumulative_cost += cost

        entry: dict[str, Any] = {
            "timestamp": time.time(),
            "model": model,
            "agent": agent,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "cumulative_cost_usd": self._cumulative_cost,
        }
        self._cost_log.append(entry)

        if self._logger is not None:
            self._logger.info(
                f"gatekeeper | model={model} in={input_tokens} out={output_tokens} "
                f"cost=${cost:.6f} cumulative=${self._cumulative_cost:.6f}"
            )

        if self._cumulative_cost > self._daily_budget:
            raise BudgetExceededError(
                f"Daily budget ${self._daily_budget:.4f} exceeded; "
                f"cumulative cost ${self._cumulative_cost:.6f}"
            )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Compute USD cost from config pricing table — no hardcoded prices."""
        prices = self._model_costs.get(model, {"input_per_million": 0.0, "output_per_million": 0.0})
        input_cost = (input_tokens / 1_000_000) * prices["input_per_million"]
        output_cost = (output_tokens / 1_000_000) * prices["output_per_million"]
        return input_cost + output_cost
