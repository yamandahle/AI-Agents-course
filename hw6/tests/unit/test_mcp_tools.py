"""Unit tests for shared MCP tool functions (tools.py) — TDD red phase."""

from unittest.mock import MagicMock

import pytest

from cop_thief.mcp.tools import (
    AuthError,
    GameContext,
    MessageTooLongError,
    check_auth,
    get_observation_dict,
    make_move_impl,
    place_barrier_impl,
    send_message_impl,
)
from cop_thief.sdk.game_engine.board import BarrierLimitError, InvalidMoveError
from cop_thief.sdk.game_engine.observation import Observation


def _make_obs(own_pos=(2, 2), opponent_pos=None, barriers=None):
    return Observation(
        agent_id="cop",
        own_position=own_pos,
        barriers=barriers or [],
        move_counter=3,
        opponent_pos=opponent_pos,
        last_message=None,
    )


def _make_ctx(agent_id="cop", max_chars=300, auth_token="secret"):
    mock_sg = MagicMock()
    mock_sg.get_observation.return_value = _make_obs()
    mock_sg.board.get_agent_pos.return_value = (2, 2)
    mock_sg.board.barriers_remaining = 4
    return GameContext(
        sub_game=mock_sg,
        agent_id=agent_id,
        message_store={"cop": None, "thief": None},
        max_message_chars=max_chars,
        auth_token=auth_token,
    )


# ── check_auth ────────────────────────────────────────────────────────────────

def test_check_auth_valid_token():
    check_auth("Bearer secret", "secret")  # must not raise


def test_check_auth_missing_token_raises():
    with pytest.raises(AuthError):
        check_auth("", "secret")


def test_check_auth_wrong_token_raises():
    with pytest.raises(AuthError):
        check_auth("Bearer wrong", "secret")


# ── get_observation_dict ──────────────────────────────────────────────────────

def test_get_observation_returns_correct_structure():
    ctx = _make_ctx()
    result = get_observation_dict(ctx)
    assert "own_position" in result
    assert "barriers" in result
    assert "move_counter" in result
    assert "opponent_pos" in result
    assert "last_message" in result


def test_get_observation_hides_opponent_outside_radius():
    ctx = _make_ctx()
    ctx.sub_game.get_observation.return_value = _make_obs(opponent_pos=None)
    assert get_observation_dict(ctx)["opponent_pos"] is None


def test_get_observation_shows_opponent_in_radius():
    ctx = _make_ctx()
    ctx.sub_game.get_observation.return_value = _make_obs(opponent_pos=(1, 3))
    assert get_observation_dict(ctx)["opponent_pos"] == [1, 3]


# ── send_message ──────────────────────────────────────────────────────────────

def test_send_message_stores_for_delivery():
    ctx = _make_ctx(agent_id="cop")
    send_message_impl(ctx, "Hello thief!")
    assert ctx.message_store["thief"] == "Hello thief!"


def test_send_message_thief_stores_for_cop():
    ctx = _make_ctx(agent_id="thief")
    send_message_impl(ctx, "You'll never catch me!")
    assert ctx.message_store["cop"] == "You'll never catch me!"


def test_send_message_too_long_returns_error():
    ctx = _make_ctx(max_chars=10)
    with pytest.raises(MessageTooLongError):
        send_message_impl(ctx, "x" * 11)


# ── make_move ─────────────────────────────────────────────────────────────────

def test_make_move_thief_valid_updates_position():
    ctx = _make_ctx(agent_id="thief")
    ctx.sub_game.board.get_agent_pos.return_value = (3, 2)
    result = make_move_impl(ctx, "S")
    ctx.sub_game.apply_thief_action.assert_called_once()
    assert result["status"] == "ok"
    assert result["new_position"] == [3, 2]


def test_make_move_cop_calls_cop_action():
    ctx = _make_ctx(agent_id="cop")
    make_move_impl(ctx, "N")
    ctx.sub_game.apply_cop_action.assert_called_once()


def test_make_move_blocked_raises_error():
    ctx = _make_ctx(agent_id="thief")
    ctx.sub_game.apply_thief_action.side_effect = InvalidMoveError("blocked")
    with pytest.raises(InvalidMoveError):
        make_move_impl(ctx, "N")


def test_make_move_unknown_direction_raises_error():
    ctx = _make_ctx(agent_id="thief")
    with pytest.raises(InvalidMoveError):
        make_move_impl(ctx, "DIAGONAL")


# ── place_barrier ─────────────────────────────────────────────────────────────

def test_place_barrier_decrements_count():
    ctx = _make_ctx(agent_id="cop")
    ctx.sub_game.board.barriers_remaining = 4
    result = place_barrier_impl(ctx)
    assert result["status"] == "ok"
    assert "barriers_remaining" in result
    assert "barrier_placed_at" in result


def test_place_barrier_at_limit_raises_error():
    ctx = _make_ctx(agent_id="cop")
    ctx.sub_game.apply_cop_action.side_effect = BarrierLimitError("at limit")
    with pytest.raises(BarrierLimitError):
        place_barrier_impl(ctx)


# ── message -> turn-log wiring (regression: messages were silently dropped) ────

def test_sent_message_flows_into_move_turn_log():
    ctx = _make_ctx(agent_id="cop")
    send_message_impl(ctx, "Closing in!")
    make_move_impl(ctx, "N")
    _, message_arg = ctx.sub_game.apply_cop_action.call_args.args
    assert message_arg == "Closing in!"


def test_sent_message_flows_into_barrier_turn_log():
    ctx = _make_ctx(agent_id="cop")
    send_message_impl(ctx, "Blocking you!")
    place_barrier_impl(ctx)
    _, message_arg = ctx.sub_game.apply_cop_action.call_args.args
    assert message_arg == "Blocking you!"


def test_pending_message_cleared_after_being_used():
    ctx = _make_ctx(agent_id="thief")
    send_message_impl(ctx, "Going north!")
    make_move_impl(ctx, "N")
    make_move_impl(ctx, "N")
    _, message_arg = ctx.sub_game.apply_thief_action.call_args.args
    assert message_arg == ""


def test_no_message_sent_still_dispatches_empty_message():
    ctx = _make_ctx(agent_id="thief")
    make_move_impl(ctx, "N")
    _, message_arg = ctx.sub_game.apply_thief_action.call_args.args
    assert message_arg == ""
