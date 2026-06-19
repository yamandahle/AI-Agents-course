from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class QueueStatus:
    """Snapshot of the request-queue depth and rate-limit counters."""

    queue_depth: int
    max_queue_depth: int
    calls_this_minute: int
    limit_per_minute: int


@dataclass
class RateLimitConfig:
    """Rate-limiting parameters for a single API provider."""

    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    retry_after_seconds: int
    max_retries: int
    queue_max_depth: int = 100


@dataclass
class ApiGatekeeper:
    """Wraps every external API call with rate limiting, concurrency control, and retry."""

    config: RateLimitConfig
    _call_times: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialise the concurrency semaphore and FIFO queue tracker from config."""
        self._semaphore = threading.Semaphore(self.config.concurrent_max)
        self._queue_depth = 0
        self._queue_lock = threading.Lock()

    def execute(self, api_call: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute api_call under rate-limit, concurrency, and retry guards."""
        self._enqueue()
        try:
            self._wait_if_rate_limited()
            with self._semaphore:
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
        finally:
            self._dequeue()

    def get_queue_status(self) -> QueueStatus:
        """Return queue depth and rate-limit counters."""
        now = time.time()
        recent = [t for t in self._call_times if now - t < 60]
        with self._queue_lock:
            depth = self._queue_depth
        return QueueStatus(
            queue_depth=depth,
            max_queue_depth=self.config.queue_max_depth,
            calls_this_minute=len(recent),
            limit_per_minute=self.config.requests_per_minute,
        )

    def _enqueue(self) -> None:
        with self._queue_lock:
            if self._queue_depth >= self.config.queue_max_depth:
                raise RuntimeError(
                    f"API queue full: {self.config.queue_max_depth} requests pending"
                )
            self._queue_depth += 1

    def _dequeue(self) -> None:
        with self._queue_lock:
            self._queue_depth = max(0, self._queue_depth - 1)

    def _wait_if_rate_limited(self) -> None:
        now = time.time()
        self._call_times = [t for t in self._call_times if now - t < 60]
        if len(self._call_times) >= self.config.requests_per_minute:
            wait = 60 - (now - self._call_times[0])
            logger.info("Rate limit reached, waiting %.1f seconds", wait)
            time.sleep(max(wait, 0))

    def _record_call(self) -> None:
        self._call_times.append(time.time())
