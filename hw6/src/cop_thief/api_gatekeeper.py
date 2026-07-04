"""Central gate for all outbound API calls: rate limiting, retries, logging."""

import asyncio
import logging
import time
from typing import Any, Callable

import httpx

logger = logging.getLogger(__name__)


class ApiCallError(Exception):
    """Raised when an API call fails on every retry attempt."""


class ApiGatekeeper:
    """Single choke point for all external API calls (LLM, Gmail, ...)."""

    def __init__(
        self, llm_config: dict, rate_limits: dict, client: httpx.AsyncClient = None
    ):
        self._base_url = llm_config["base_url"]
        self._timeout = llm_config["timeout_seconds"]
        self._rate_limits = rate_limits
        self._client = client or httpx.AsyncClient()
        self._call_times: dict[str, list[float]] = {}

    async def call(self, endpoint: str, payload: dict) -> dict:
        """POST payload to the LLM endpoint, retrying on failure; return JSON."""
        max_retries = self._rate_limits["ollama"]["max_retries"]
        await self._throttle("ollama")
        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                response = await self._client.post(
                    f"{self._base_url}{endpoint}", json=payload, timeout=self._timeout
                )
                response.raise_for_status()
                self._record_call("ollama")
                logger.info("ApiGatekeeper call ok: %s (attempt %d)", endpoint, attempt)
                return response.json()
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "ApiGatekeeper call failed: %s (attempt %d/%d): %s",
                    endpoint, attempt, max_retries, exc,
                )
        raise ApiCallError(
            f"All {max_retries} attempts failed for {endpoint}"
        ) from last_error

    async def call_sync(self, provider: str, func: Callable[[], Any]) -> Any:
        """Run a blocking callable (e.g. Gmail SDK) under the same rate-limit,
        retry, and logging policy as `call()`, without needing httpx/async."""
        max_retries = self._rate_limits[provider]["max_retries"]
        await self._throttle(provider)
        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                result = await asyncio.to_thread(func)
                self._record_call(provider)
                logger.info("ApiGatekeeper %s call ok (attempt %d)", provider, attempt)
                return result
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "ApiGatekeeper %s call failed (attempt %d/%d): %s",
                    provider, attempt, max_retries, exc,
                )
        raise ApiCallError(
            f"All {max_retries} attempts failed for {provider}"
        ) from last_error

    def _record_call(self, provider: str) -> None:
        self._call_times.setdefault(provider, []).append(time.monotonic())

    async def _throttle(self, provider: str) -> None:
        """Sleep if calling now would exceed the provider's calls_per_minute."""
        now = time.monotonic()
        times = [t for t in self._call_times.get(provider, []) if now - t < 60]
        self._call_times[provider] = times
        limit = self._rate_limits[provider]["calls_per_minute"]
        if len(times) >= limit:
            sleep_for = 60 - (now - times[0])
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
