"""Unit tests for the Cop MCP server — TDD red phase."""

from unittest.mock import MagicMock

import pytest
from fastmcp import Client

import cop_thief.mcp.cop_server as cop_server
from cop_thief.mcp.tools import AuthError, GameContext, check_auth
from cop_thief.sdk.game_engine.observation import Observation


def _make_obs():
    return Observation("cop", (2, 2), [], 3, None, None)


def _mock_ctx(agent_id="cop"):
    mock_sg = MagicMock()
    mock_sg.get_observation.return_value = _make_obs()
    mock_sg.board.get_agent_pos.return_value = (2, 2)
    mock_sg.board.barriers_remaining = 4
    return GameContext(
        sub_game=mock_sg,
        agent_id=agent_id,
        message_store={"cop": None, "thief": None},
        max_message_chars=300,
        auth_token="test-token",
    )


@pytest.fixture(autouse=True)
def reset_ctx():
    cop_server.clear_context()
    yield
    cop_server.clear_context()


# ── tool registry ─────────────────────────────────────────────────────────────

async def test_cop_server_has_place_barrier():
    async with Client(cop_server.mcp) as client:
        tools = await client.list_tools()
        names = [t.name for t in tools]
        assert "place_barrier" in names


async def test_cop_server_has_4_tools():
    async with Client(cop_server.mcp) as client:
        tools = await client.list_tools()
        assert len(tools) == 4


# ── auth (tested via check_auth, which the server delegates to) ───────────────

def test_missing_token_returns_401():
    with pytest.raises(AuthError):
        check_auth("", "secret")


def test_invalid_token_returns_401():
    with pytest.raises(AuthError):
        check_auth("Bearer wrong", "secret")


# ── tool execution ────────────────────────────────────────────────────────────

async def test_valid_context_get_observation_succeeds():
    cop_server.set_context(_mock_ctx())
    async with Client(cop_server.mcp) as client:
        result = await client.call_tool("get_observation", {})
    assert result is not None


async def test_no_context_raises_error():
    async with Client(cop_server.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool("get_observation", {})


async def test_send_message_stores_message():
    cop_server.set_context(_mock_ctx())
    async with Client(cop_server.mcp) as client:
        await client.call_tool("send_message", {"message": "I see you!"})
    ctx = cop_server._ctx
    assert ctx.message_store["thief"] == "I see you!"
