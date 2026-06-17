from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    retry_after_seconds: int
    max_retries: int


@dataclass
class ApiGatekeeper:
    config: RateLimitConfig
    _call_times: list[float] = field(default_factory=list)

    def execute(self, api_call: Callable, *args: Any, **kwargs: Any) -> Any:
        self._wait_if_rate_limited()
        for attempt in range(self.config.max_retries):
            try:
                result = api_call(*args, **kwargs)
                self._record_call()
                logger.info("API call succeeded on attempt %d", attempt + 1)
                return result
            except Exception as exc:
                logger.warning("Attempt %d failed: %s", attempt + 1, exc)
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_after_seconds)
                else:
                    raise

    def _wait_if_rate_limited(self) -> None:
        now = time.time()
        self._call_times = [t for t in self._call_times if now - t < 60]
        if len(self._call_times) >= self.config.requests_per_minute:
            wait = 60 - (now - self._call_times[0])
            logger.info("Rate limit reached, waiting %.1f seconds", wait)
            time.sleep(max(wait, 0))

    def _record_call(self) -> None:
        self._call_times.append(time.time())
