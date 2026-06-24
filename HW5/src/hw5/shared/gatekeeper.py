"""ApiGatekeeper — token-bucket rate limiter wrapping any callable."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

log = logging.getLogger(__name__)

_T = TypeVar("_T")
_DEFAULT_RATE: float = 5.0
_DEFAULT_BURST: int = 10


class ApiGatekeeper:
    """Thread-safe token-bucket rate limiter.

    Wraps callables via execute() to enforce a maximum requests-per-second rate.
    """

    def __init__(
        self, rate: float = _DEFAULT_RATE, burst: int = _DEFAULT_BURST
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be > 0")
        self._rate = rate
        self._burst = burst
        self._tokens: float = float(burst)
        self._last_refill: float = time.monotonic()
        self._lock = threading.Lock()

    @classmethod
    def from_config(
        cls, path: str, key: str = "huggingface_download_rps"
    ) -> ApiGatekeeper:
        """Instantiate by reading a rate from a rate_limits.json file."""
        data: dict[str, Any] = json.loads(Path(path).read_text())
        return cls(rate=float(data.get(key, _DEFAULT_RATE)))

    def execute(self, fn: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
        """Block until a token is available, then invoke fn(*args, **kwargs)."""
        self._acquire()
        return fn(*args, **kwargs)

    def set_rate(self, new_rate: float) -> None:
        """Change the token refill rate at runtime (requests per second)."""
        if new_rate <= 0:
            raise ValueError("rate must be > 0")
        with self._lock:
            self._rate = new_rate

    def reset(self) -> None:
        """Refill the bucket to burst capacity — intended for test isolation."""
        with self._lock:
            self._tokens = float(self._burst)
            self._last_refill = time.monotonic()

    def __enter__(self) -> ApiGatekeeper:
        """Acquire a token on context entry."""
        self._acquire()
        return self

    def __exit__(self, *_: Any) -> None:
        pass

    def _acquire(self) -> None:
        with self._lock:
            self._refill()
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self._rate
                log.debug("Gatekeeper: waiting %.0fms for rate limit", wait * 1000)
                time.sleep(wait)
                self._refill()
            self._tokens -= 1.0

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(float(self._burst), self._tokens + elapsed * self._rate)
        self._last_refill = now
