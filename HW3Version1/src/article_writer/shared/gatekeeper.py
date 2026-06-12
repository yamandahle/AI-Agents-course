"""API Gatekeeper — centralized rate limiting, queuing, retry logic, and logging."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from article_writer.shared.config import load_rate_limits
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)


@dataclass
class QueueStatus:
    queue_depth: int
    active_calls: int


@dataclass
class _ServiceState:
    rpm_calls: deque = field(default_factory=deque)
    rph_calls: deque = field(default_factory=deque)
    active: int = 0


class ApiGatekeeper:
    """All external API calls must pass through this class."""

    def __init__(self) -> None:
        self._limits = load_rate_limits()
        self._state: dict[str, _ServiceState] = {}

    def _limits_for(self, service: str) -> dict:
        return self._limits.get(service, self._limits["default"])

    def _state_for(self, service: str) -> _ServiceState:
        if service not in self._state:
            self._state[service] = _ServiceState()
        return self._state[service]

    def _seconds_to_wait(self, service: str) -> float:
        limits = self._limits_for(service)
        state = self._state_for(service)
        now = time.monotonic()
        while state.rpm_calls and now - state.rpm_calls[0] > 60:
            state.rpm_calls.popleft()
        while state.rph_calls and now - state.rph_calls[0] > 3600:
            state.rph_calls.popleft()
        if len(state.rpm_calls) >= limits["requests_per_minute"]:
            return 60.0 - (now - state.rpm_calls[0])
        if len(state.rph_calls) >= limits["requests_per_hour"]:
            return 3600.0 - (now - state.rph_calls[0])
        if state.active >= limits["concurrent_max"]:
            return float(limits["retry_after_seconds"])
        return 0.0

    def execute(
        self, service: str, api_call: Callable, *args: Any, **kwargs: Any
    ) -> Any:
        """Execute api_call with rate limiting, retry, and logging."""
        limits = self._limits_for(service)
        state = self._state_for(service)
        wait = self._seconds_to_wait(service)
        if wait > 0:
            logger.info("Rate limit hit — waiting %.1fs for %s", wait, service)
            time.sleep(wait)
        state.active += 1
        now = time.monotonic()
        state.rpm_calls.append(now)
        state.rph_calls.append(now)
        last_exc: Exception | None = None
        try:
            for attempt in range(1, limits["max_retries"] + 1):
                try:
                    result = api_call(*args, **kwargs)
                    logger.log_api_call(service, str(args)[:80], str(result)[:120])
                    return result
                except Exception as exc:
                    last_exc = exc
                    logger.warning("Attempt %d/%d failed for %s: %s", attempt, limits["max_retries"], service, exc)
                    if attempt < limits["max_retries"]:
                        time.sleep(limits["retry_after_seconds"])
        finally:
            state.active -= 1
        raise RuntimeError(f"All retries exhausted for {service}") from last_exc

    def get_queue_status(self) -> QueueStatus:
        total_active = sum(s.active for s in self._state.values())
        return QueueStatus(queue_depth=0, active_calls=total_active)
