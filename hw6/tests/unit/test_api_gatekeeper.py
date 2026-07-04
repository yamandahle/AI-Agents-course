"""Unit tests for ApiGatekeeper — TDD red phase."""

import logging
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from cop_thief import api_gatekeeper as gatekeeper_module
from cop_thief.api_gatekeeper import ApiCallError, ApiGatekeeper

LLM_CONFIG = {
    "base_url": "http://localhost:11434",
    "timeout_seconds": 30,
}
RATE_LIMITS = {"ollama": {"calls_per_minute": 30, "max_retries": 3}}


def _ok_response(data: dict) -> MagicMock:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = data
    return response


async def test_call_succeeds_on_first_try():
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=_ok_response({"message": "hi"}))
    gatekeeper = ApiGatekeeper(LLM_CONFIG, RATE_LIMITS, client=mock_client)

    result = await gatekeeper.call("/api/chat", {"model": "phi3:mini"})

    assert result == {"message": "hi"}
    assert mock_client.post.call_count == 1


async def test_call_retries_on_failure():
    mock_client = MagicMock()
    mock_client.post = AsyncMock(
        side_effect=[httpx.ConnectError("boom"), _ok_response({"ok": True})]
    )
    gatekeeper = ApiGatekeeper(LLM_CONFIG, RATE_LIMITS, client=mock_client)

    result = await gatekeeper.call("/api/chat", {})

    assert result == {"ok": True}
    assert mock_client.post.call_count == 2


async def test_call_raises_after_max_retries():
    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=httpx.ConnectError("boom"))
    limits = {"ollama": {"calls_per_minute": 30, "max_retries": 2}}
    gatekeeper = ApiGatekeeper(LLM_CONFIG, limits, client=mock_client)

    with pytest.raises(ApiCallError):
        await gatekeeper.call("/api/chat", {})

    assert mock_client.post.call_count == 2


async def test_call_is_logged(caplog):
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=_ok_response({"ok": True}))
    gatekeeper = ApiGatekeeper(LLM_CONFIG, RATE_LIMITS, client=mock_client)

    with caplog.at_level(logging.INFO):
        await gatekeeper.call("/api/chat", {})

    assert any("/api/chat" in record.message for record in caplog.records)


async def test_throttle_sleeps_when_limit_exceeded(monkeypatch):
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=_ok_response({"ok": True}))
    limits = {"ollama": {"calls_per_minute": 1, "max_retries": 3}}
    gatekeeper = ApiGatekeeper(LLM_CONFIG, limits, client=mock_client)
    gatekeeper._call_times = [gatekeeper_module.time.monotonic()]

    sleep_mock = AsyncMock()
    monkeypatch.setattr(gatekeeper_module.asyncio, "sleep", sleep_mock)

    await gatekeeper.call("/api/chat", {})

    sleep_mock.assert_awaited_once()
