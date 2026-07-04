"""Central gate for all outbound LLM calls: rate limiting, retries, logging."""

import asyncio
import logging
import time

import httpx

logger = logging.getLogger(__name__)


class ApiCallError(Exception):
    """Raised when an API call fails on every retry attempt."""


class ApiGatekeeper:
    """Single choke point for LLM API calls (currently: Ollama)."""

    def __init__(
        self, llm_config: dict, rate_limits: dict, client: httpx.AsyncClient = None
    ):
        self._base_url = llm_config["base_url"]
        self._timeout = llm_config["timeout_seconds"]
        self._calls_per_minute = rate_limits["ollama"]["calls_per_minute"]
        self._max_retries = rate_limits["ollama"]["max_retries"]
        self._client = client or httpx.AsyncClient()
        self._call_times: list[float] = []

    async def call(self, endpoint: str, payload: dict) -> dict:
        """POST payload to endpoint, retrying on failure, and return parsed JSON."""
        await self._throttle()
        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                response = await self._client.post(
                    f"{self._base_url}{endpoint}", json=payload, timeout=self._timeout
                )
                response.raise_for_status()
                self._call_times.append(time.monotonic())
                logger.info("ApiGatekeeper call ok: %s (attempt %d)", endpoint, attempt)
                return response.json()
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "ApiGatekeeper call failed: %s (attempt %d/%d): %s",
                    endpoint, attempt, self._max_retries, exc,
                )
        raise ApiCallError(
            f"All {self._max_retries} attempts failed for {endpoint}"
        ) from last_error

    async def _throttle(self) -> None:
        """Sleep if calling now would exceed calls_per_minute."""
        now = time.monotonic()
        self._call_times = [t for t in self._call_times if now - t < 60]
        if len(self._call_times) >= self._calls_per_minute:
            sleep_for = 60 - (now - self._call_times[0])
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
