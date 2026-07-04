"""Unit tests for action_parser — TDD red phase."""

import pytest

from cop_thief.orchestrator.action_parser import parse_response
from cop_thief.sdk.game_engine.board import Direction

ALL_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def test_parse_direction_north():
    message, action = parse_response("MESSAGE: Closing in!\nACTION: N")
    assert action.direction == Direction.N


@pytest.mark.parametrize("direction", ALL_DIRECTIONS)
def test_parse_all_8_directions(direction):
    message, action = parse_response(f"MESSAGE: hi\nACTION: {direction}")
    assert action.direction == Direction[direction]


def test_parse_barrier_action():
    message, action = parse_response("MESSAGE: Blocking you!\nACTION: BARRIER")
    assert action.direction is None


def test_parse_case_insensitive():
    message, action = parse_response("message: hello\naction: se")
    assert action.direction == Direction.SE


def test_parse_invalid_returns_none():
    message, action = parse_response("MESSAGE: confused\nACTION: DIAGONAL")
    assert action is None


def test_parse_message_extracted():
    message, action = parse_response("MESSAGE: I am closing in!\nACTION: SE")
    assert message == "I am closing in!"
