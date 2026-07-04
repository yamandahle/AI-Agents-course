"""Unit tests for the Thief MCP server — TDD red phase."""

from unittest.mock import MagicMock

import pytest
from fastmcp import Client

import cop_thief.mcp.thief_server as thief_server
from cop_thief.mcp.tools import AuthError, GameContext, check_auth
from cop_thief.sdk.game_engine.observation import Observation


def _make_obs():
    return Observation("thief", (3, 3), [], 3, None, None)


def _mock_ctx(agent_id="thief"):
    mock_sg = MagicMock()
    mock_sg.get_observation.return_value = _make_obs()
    mock_sg.board.get_agent_pos.return_value = (3, 3)
    return GameContext(
        sub_game=mock_sg,
        agent_id=agent_id,
        message_store={"cop": None, "thief": None},
        max_message_chars=300,
        auth_token="test-token",
    )


@pytest.fixture(autouse=True)
def reset_ctx():
    thief_server.clear_context()
    yield
    thief_server.clear_context()


# ── tool registry ─────────────────────────────────────────────────────────────

async def test_thief_server_has_no_place_barrier():
    async with Client(thief_server.mcp) as client:
        tools = await client.list_tools()
        names = [t.name for t in tools]
        assert "place_barrier" not in names


async def test_thief_server_has_3_tools():
    async with Client(thief_server.mcp) as client:
        tools = await client.list_tools()
        assert len(tools) == 3


# ── auth: check_auth() in isolation ────────────────────────────────────────────

def test_missing_token_returns_401():
    with pytest.raises(AuthError):
        check_auth("", "secret")


def test_valid_token_passes():
    check_auth("Bearer secret", "secret")  # must not raise


# ── auth: enforced on the real FastMCP tool-call path ──────────────────────────

async def test_tool_call_missing_token_raises():
    thief_server.set_context(_mock_ctx())
    async with Client(thief_server.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool("get_observation", {})


async def test_tool_call_wrong_token_raises():
    thief_server.set_context(_mock_ctx())
    async with Client(thief_server.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool(
                "get_observation", {"authorization": "Bearer wrong-token"}
            )


async def test_tool_call_valid_token_succeeds():
    thief_server.set_context(_mock_ctx())
    async with Client(thief_server.mcp) as client:
        result = await client.call_tool(
            "get_observation", {"authorization": "Bearer test-token"}
        )
    assert result is not None


# ── tool execution ────────────────────────────────────────────────────────────

async def test_valid_context_get_observation_succeeds():
    thief_server.set_context(_mock_ctx())
    async with Client(thief_server.mcp) as client:
        result = await client.call_tool(
            "get_observation", {"authorization": "Bearer test-token"}
        )
    assert result is not None


async def test_no_context_raises_error():
    async with Client(thief_server.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool(
                "get_observation", {"authorization": "Bearer test-token"}
            )
