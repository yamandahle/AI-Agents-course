"""Integration tests for GameLoop — TDD red phase.

Uses real SubGame + real MCP servers (in-process, no network) so tool calls
genuinely mutate shared state, exactly like a live game. Only the LLM
boundary (ApiGatekeeper) is mocked, per the PRD's test plan.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

import cop_thief.mcp.cop_server as cop_server
import cop_thief.mcp.thief_server as thief_server
import cop_thief.orchestrator.game_loop as game_loop_module
from cop_thief.mcp.tools import GameContext
from cop_thief.orchestrator.fallback import random_starts
from cop_thief.orchestrator.game_loop import GameLoop
from cop_thief.orchestrator.mcp_client import McpClient
from cop_thief.sdk.game_engine.game_session import TooManyCrashesError
from cop_thief.sdk.game_engine.sub_game import SubGame

AUTH_TOKEN = "tok"
SAFE_STARTS = ((4, 4), (4, 5))  # centre of an 8x8 grid: every direction is in-bounds


def _config(rows=8, cols=8, max_moves=1, num_games=1, max_retries=3):
    return {
        "grid": {"rows": rows, "cols": cols},
        "game": {"max_moves": max_moves, "max_barriers": 5, "num_games": num_games},
        "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
        "vision": {"cop_vision_radius": 5, "thief_vision_radius": 5},
        "communication": {"max_message_chars": 300},
        "llm": {
            "provider": "ollama", "model": "phi3:mini",
            "base_url": "http://localhost:11434",
            "timeout_seconds": 30, "max_retries": max_retries,
        },
    }


@pytest.fixture(autouse=True)
def reset_servers():
    cop_server.clear_context()
    thief_server.clear_context()
    yield
    cop_server.clear_context()
    thief_server.clear_context()


def _make_loop(config, gatekeeper, starts=SAFE_STARTS):
    sg = SubGame(
        rows=config["grid"]["rows"], cols=config["grid"]["cols"],
        max_moves=config["game"]["max_moves"],
        max_barriers=config["game"]["max_barriers"],
        cop_vision_radius=config["vision"]["cop_vision_radius"],
        thief_vision_radius=config["vision"]["thief_vision_radius"],
        scoring=config["scoring"],
    )
    store = {"cop": None, "thief": None}
    cop_server.set_context(GameContext(sg, "cop", store, 300, AUTH_TOKEN))
    thief_server.set_context(GameContext(sg, "thief", store, 300, AUTH_TOKEN))
    cop_client = McpClient(cop_server.mcp, auth_token=AUTH_TOKEN)
    thief_client = McpClient(thief_server.mcp, auth_token=AUTH_TOKEN)
    loop = GameLoop(config, sg, cop_client, thief_client, gatekeeper)
    game_loop_module.random_starts = lambda cfg: starts
    return loop, sg


def _fake_gatekeeper(*replies: str):
    """A stand-in ApiGatekeeper whose .call() returns each reply in sequence."""
    gatekeeper = AsyncMock()
    ollama_replies = [{"message": {"content": r}} for r in replies]
    gatekeeper.call = AsyncMock(side_effect=ollama_replies)
    return gatekeeper


async def test_thief_moves_before_cop():
    config = _config()
    gatekeeper = _fake_gatekeeper("MESSAGE: hi\nACTION: N", "MESSAGE: hi\nACTION: N")
    loop, sg = _make_loop(config, gatekeeper)
    call_order = []
    orig_thief = loop._clients["thief"].get_observation
    orig_cop = loop._clients["cop"].get_observation

    async def spy_thief():
        call_order.append("thief")
        return await orig_thief()

    async def spy_cop():
        call_order.append("cop")
        return await orig_cop()

    loop._clients["thief"].get_observation = spy_thief
    loop._clients["cop"].get_observation = spy_cop

    await loop.run()

    assert call_order == ["thief", "cop"]


async def test_turn_calls_get_observation_then_move():
    config = _config()
    gatekeeper = _fake_gatekeeper("MESSAGE: hi\nACTION: N", "MESSAGE: hi\nACTION: N")
    loop, sg = _make_loop(config, gatekeeper)
    calls = []
    cop_client = loop._clients["cop"]
    orig_obs, orig_msg, orig_move = (
        cop_client.get_observation, cop_client.send_message, cop_client.make_move,
    )

    async def spy_obs():
        calls.append("get_observation")
        return await orig_obs()

    async def spy_msg(message):
        calls.append("send_message")
        return await orig_msg(message)

    async def spy_move(direction):
        calls.append("make_move")
        return await orig_move(direction)

    cop_client.get_observation, cop_client.send_message, cop_client.make_move = (
        spy_obs, spy_msg, spy_move,
    )

    await loop.run()

    assert calls == ["get_observation", "send_message", "make_move"]


async def test_loop_stops_on_cop_win():
    config = _config(rows=3, cols=3, max_moves=25)
    # cop=(0,0), thief=(1,0). Thief moves E -> (1,1). Cop moves SE -> (1,1): capture.
    gatekeeper = _fake_gatekeeper(
        "MESSAGE: hi\nACTION: E",
        "MESSAGE: hi\nACTION: SE",
    )
    loop, sg = _make_loop(config, gatekeeper, starts=((0, 0), (1, 0)))

    result = await loop.run()

    assert result.sub_games[0].winner == "cop"


async def test_loop_stops_on_thief_win():
    config = _config(max_moves=1)
    # No capture on the only turn -> move_counter hits max_moves -> thief wins.
    gatekeeper = _fake_gatekeeper("MESSAGE: hi\nACTION: S", "MESSAGE: hi\nACTION: N")
    loop, sg = _make_loop(config, gatekeeper)

    result = await loop.run()

    assert result.sub_games[0].winner == "thief"


async def test_six_sub_games_trigger_report():
    config = _config(max_moves=1, num_games=6)
    replies = ["MESSAGE: hi\nACTION: S", "MESSAGE: hi\nACTION: N"] * 6
    gatekeeper = _fake_gatekeeper(*replies)
    loop, sg = _make_loop(config, gatekeeper)

    received = []
    result = await loop.run(on_complete=received.append)

    assert len(received) == 1
    assert received[0] is result
    assert result.totals["thief"] == 10 * 6


async def test_invalid_action_triggers_retry():
    config = _config(max_retries=3)
    gatekeeper = _fake_gatekeeper(
        "garbage, no action here",       # thief: bad parse -> retry
        "MESSAGE: hi\nACTION: S",        # thief: good on retry
        "MESSAGE: hi\nACTION: N",        # cop: good first try
    )
    loop, sg = _make_loop(config, gatekeeper)

    await loop.run()

    assert gatekeeper.call.await_count == 3


async def test_all_retries_fail_triggers_fallback(caplog):
    config = _config(max_retries=2)
    gatekeeper = _fake_gatekeeper(*(["garbage"] * 4))
    loop, sg = _make_loop(config, gatekeeper)

    result = await loop.run()

    assert gatekeeper.call.await_count == 4
    assert result.sub_games[0].moves_played == 1
    assert any("fallback" in r.message.lower() for r in caplog.records)


async def test_cop_barrier_action_calls_place_barrier():
    config = _config(max_moves=1)
    gatekeeper = _fake_gatekeeper(
        "MESSAGE: hi\nACTION: N", "MESSAGE: hi\nACTION: BARRIER",
    )
    loop, sg = _make_loop(config, gatekeeper)

    result = await loop.run()

    assert result.sub_games[0].barriers_placed == 1


async def test_crashed_sub_game_is_marked_and_retried():
    config = _config(max_moves=1, num_games=1)
    gatekeeper = AsyncMock()
    gatekeeper.call = AsyncMock(
        side_effect=[
            RuntimeError("simulated LLM outage"),
            {"message": {"content": "MESSAGE: hi\nACTION: S"}},
            {"message": {"content": "MESSAGE: hi\nACTION: N"}},
        ]
    )
    loop, sg = _make_loop(config, gatekeeper)

    result = await loop.run()

    assert len(result.sub_games) == 1
    assert not result.sub_games[0].crashed


async def test_too_many_crashes_raises():
    config = _config(max_moves=1, num_games=1)
    gatekeeper = AsyncMock()
    gatekeeper.call = AsyncMock(side_effect=RuntimeError("always fails"))
    loop, sg = _make_loop(config, gatekeeper)

    with pytest.raises(TooManyCrashesError):
        await loop.run()


async def test_invalid_move_rejected_by_server_triggers_retry():
    config = _config(rows=3, cols=2, max_moves=1, max_retries=3)
    # Thief at (0,0): N is out of bounds -> rejected, retried; then S succeeds.
    # Cop at (2,1): N is in-bounds -> succeeds first try.
    gatekeeper = _fake_gatekeeper(
        "MESSAGE: hi\nACTION: N",
        "MESSAGE: hi\nACTION: S",
        "MESSAGE: hi\nACTION: N",
    )
    loop, sg = _make_loop(config, gatekeeper, starts=((2, 1), (0, 0)))

    await loop.run()

    assert gatekeeper.call.await_count == 3


async def test_message_truncated_to_configured_max_chars():
    config = _config(max_moves=1)
    config["communication"]["max_message_chars"] = 10
    long_message = "M" * 50
    gatekeeper = _fake_gatekeeper(
        f"MESSAGE: {long_message}\nACTION: S",
        "MESSAGE: hi\nACTION: N",
    )
    loop, sg = _make_loop(config, gatekeeper)

    await loop.run()  # must not raise MessageTooLongError


def test_random_starts_returns_two_distinct_in_bounds_cells():
    config = _config(rows=4, cols=4)

    cop_start, thief_start = random_starts(config)

    assert cop_start != thief_start
    for row, col in (cop_start, thief_start):
        assert 0 <= row < 4
        assert 0 <= col < 4


async def test_q_hint_injected_into_cop_prompt_only():
    config = _config(max_moves=1)
    gatekeeper = _fake_gatekeeper("MESSAGE: hi\nACTION: N", "MESSAGE: hi\nACTION: N")
    advisor = MagicMock()
    advisor.get_hint.return_value = "Position analysis suggests moving north."
    sg = SubGame(
        rows=config["grid"]["rows"], cols=config["grid"]["cols"],
        max_moves=config["game"]["max_moves"],
        max_barriers=config["game"]["max_barriers"],
        cop_vision_radius=config["vision"]["cop_vision_radius"],
        thief_vision_radius=config["vision"]["thief_vision_radius"],
        scoring=config["scoring"],
    )
    store = {"cop": None, "thief": None}
    cop_server.set_context(GameContext(sg, "cop", store, 300, AUTH_TOKEN))
    thief_server.set_context(GameContext(sg, "thief", store, 300, AUTH_TOKEN))
    cop_client = McpClient(cop_server.mcp, auth_token=AUTH_TOKEN)
    thief_client = McpClient(thief_server.mcp, auth_token=AUTH_TOKEN)
    loop = GameLoop(config, sg, cop_client, thief_client, gatekeeper, advisor=advisor)
    game_loop_module.random_starts = lambda cfg: SAFE_STARTS

    await loop.run()

    prompts = [
        call.args[1]["messages"][1]["content"]
        for call in gatekeeper.call.await_args_list
    ]
    assert "Position analysis suggests moving north." not in prompts[0]  # thief
    assert "Position analysis suggests moving north." in prompts[1]  # cop


async def test_on_turn_hook_receives_game_state_each_turn():
    config = _config(max_moves=1)
    gatekeeper = _fake_gatekeeper("MESSAGE: hi\nACTION: N", "MESSAGE: hi\nACTION: N")
    loop, sg = _make_loop(config, gatekeeper)
    received = []

    await loop.run(on_turn=received.append)

    assert [s.current_turn for s in received] == ["thief", "cop"]
    assert received[0].sub_game_number == 1
    assert received[1].cop_position == sg.board.get_agent_pos("cop")
    assert received[1].thief_position == sg.board.get_agent_pos("thief")
