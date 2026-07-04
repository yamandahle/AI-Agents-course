"""Unit tests for the orchestrator's MCP client wrapper — TDD red phase."""

from unittest.mock import AsyncMock, MagicMock

import cop_thief.orchestrator.mcp_client as mcp_client_module
from cop_thief.orchestrator.mcp_client import McpClient, build_client


def _mock_client(data: dict):
    instance = MagicMock()
    instance.__aenter__ = AsyncMock(return_value=instance)
    instance.__aexit__ = AsyncMock(return_value=False)
    result = MagicMock()
    result.data = data
    instance.call_tool = AsyncMock(return_value=result)
    client_class = MagicMock(return_value=instance)
    return client_class, instance


async def test_get_observation_calls_correct_server(monkeypatch):
    client_class, instance = _mock_client({"own_position": [0, 0]})
    monkeypatch.setattr(mcp_client_module, "Client", client_class)

    client = McpClient("http://127.0.0.1:8001/mcp", auth_token="tok")
    result = await client.get_observation()

    client_class.assert_called_once_with("http://127.0.0.1:8001/mcp")
    instance.call_tool.assert_awaited_once_with(
        "get_observation", {"authorization": "Bearer tok"}
    )
    assert result == {"own_position": [0, 0]}


async def test_make_move_sends_direction(monkeypatch):
    client_class, instance = _mock_client({"status": "ok"})
    monkeypatch.setattr(mcp_client_module, "Client", client_class)

    client = McpClient("http://127.0.0.1:8002/mcp", auth_token="tok")
    await client.make_move("SE")

    instance.call_tool.assert_awaited_once_with(
        "make_move", {"direction": "SE", "authorization": "Bearer tok"}
    )


async def test_send_message_posts_to_server(monkeypatch):
    client_class, instance = _mock_client({"status": "ok"})
    monkeypatch.setattr(mcp_client_module, "Client", client_class)

    client = McpClient("http://127.0.0.1:8001/mcp", auth_token="tok")
    await client.send_message("hello")

    instance.call_tool.assert_awaited_once_with(
        "send_message", {"message": "hello", "authorization": "Bearer tok"}
    )


async def test_place_barrier_calls_cop_server(monkeypatch):
    client_class, instance = _mock_client({"status": "ok"})
    monkeypatch.setattr(mcp_client_module, "Client", client_class)

    client = McpClient("http://127.0.0.1:8001/mcp", auth_token="tok")
    await client.place_barrier()

    client_class.assert_called_once_with("http://127.0.0.1:8001/mcp")
    instance.call_tool.assert_awaited_once_with(
        "place_barrier", {"authorization": "Bearer tok"}
    )


def test_build_client_uses_config_port():
    config = {"mcp": {"cop_port": 8001, "thief_port": 8002}}
    cop_client = build_client("cop", config, auth_token="tok")
    thief_client = build_client("thief", config, auth_token="tok")
    assert cop_client.base_url == "http://127.0.0.1:8001/mcp"
    assert thief_client.base_url == "http://127.0.0.1:8002/mcp"


# ── Connection reuse (Gap 7 regression) ─────────────────────────────────────────


async def test_connection_reused_across_multiple_calls(monkeypatch):
    """One Client must be built and entered once, reused for several tool calls."""
    client_class, instance = _mock_client({"status": "ok"})
    monkeypatch.setattr(mcp_client_module, "Client", client_class)

    client = McpClient("http://127.0.0.1:8001/mcp", auth_token="tok")
    await client.connect()
    await client.get_observation()
    await client.send_message("hi")
    await client.make_move("N")
    await client.place_barrier()
    await client.close()

    client_class.assert_called_once_with("http://127.0.0.1:8001/mcp")
    instance.__aenter__.assert_awaited_once()
    instance.__aexit__.assert_awaited_once()
    assert instance.call_tool.await_count == 4
