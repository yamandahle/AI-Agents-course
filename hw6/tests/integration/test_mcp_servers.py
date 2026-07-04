"""Integration tests: both MCP servers working with a shared game context."""

import pytest
from fastmcp import Client

import cop_thief.mcp.cop_server as cop_server
import cop_thief.mcp.thief_server as thief_server
from cop_thief.mcp.tools import GameContext
from cop_thief.sdk.game_engine.sub_game import SubGame

CONFIG = {
    "grid": {"rows": 5, "cols": 5},
    "game": {"max_moves": 25, "num_games": 3, "max_barriers": 5},
    "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    "vision": {"cop_vision_radius": 4, "thief_vision_radius": 4},
    "communication": {"max_message_chars": 300},
}

SHARED_MSG_STORE = {"cop": None, "thief": None}


def _make_sub_game():
    sg = SubGame(
        rows=5, cols=5, max_moves=25, max_barriers=5,
        cop_vision_radius=4, thief_vision_radius=4,
        scoring=CONFIG["scoring"],
    )
    sg.reset((1, 1), (3, 3))
    return sg


@pytest.fixture(autouse=True)
def reset_servers():
    cop_server.clear_context()
    thief_server.clear_context()
    yield
    cop_server.clear_context()
    thief_server.clear_context()


# ── tool registry ─────────────────────────────────────────────────────────────

async def test_cop_server_has_place_barrier():
    async with Client(cop_server.mcp) as client:
        tools = await client.list_tools()
        assert any(t.name == "place_barrier" for t in tools)


async def test_thief_server_has_no_place_barrier():
    async with Client(thief_server.mcp) as client:
        tools = await client.list_tools()
        assert not any(t.name == "place_barrier" for t in tools)


# ── round-trip pipeline ───────────────────────────────────────────────────────

async def test_full_tool_round_trip():
    """Thief observes → sends message → moves. Cop observes (sees message) → moves."""
    sg = _make_sub_game()
    store = {"cop": None, "thief": None}

    cop_server.set_context(GameContext(
        sub_game=sg, agent_id="cop",
        message_store=store, max_message_chars=300, auth_token="tok",
    ))
    thief_server.set_context(GameContext(
        sub_game=sg, agent_id="thief",
        message_store=store, max_message_chars=300, auth_token="tok",
    ))

    async with Client(thief_server.mcp) as t_client:
        obs = await t_client.call_tool("get_observation", {})
        assert obs is not None
        await t_client.call_tool("send_message", {"message": "You can't catch me!"})
        assert store["cop"] == "You can't catch me!"
        await t_client.call_tool("make_move", {"direction": "S"})

    async with Client(cop_server.mcp) as c_client:
        obs = await c_client.call_tool("get_observation", {})
        assert obs is not None
        await c_client.call_tool("make_move", {"direction": "N"})


async def test_message_delivered_in_observation():
    """A message sent by thief appears in cop's next observation."""
    sg = _make_sub_game()
    store = {"cop": None, "thief": None}

    cop_ctx = GameContext(
        sub_game=sg, agent_id="cop",
        message_store=store, max_message_chars=300, auth_token="tok",
    )
    thief_ctx = GameContext(
        sub_game=sg, agent_id="thief",
        message_store=store, max_message_chars=300, auth_token="tok",
    )
    cop_server.set_context(cop_ctx)
    thief_server.set_context(thief_ctx)

    async with Client(thief_server.mcp) as t_client:
        await t_client.call_tool("send_message", {"message": "Going north!"})

    assert store["cop"] == "Going north!"
