"""Unit tests for ObservationEngine — TDD red phase."""

import pytest

from cop_thief.sdk.game_engine.board import GameBoard
from cop_thief.sdk.game_engine.observation import Observation, ObservationEngine


@pytest.fixture
def board():
    """5x5 board with cop at (2,2) and thief at (4,4)."""
    b = GameBoard(rows=5, cols=5, max_barriers=5)
    b.place_agent("cop", 2, 2)
    b.place_agent("thief", 4, 4)
    return b


@pytest.fixture
def engine():
    """ObservationEngine with vision radius 2 for both agents."""
    return ObservationEngine(cop_vision_radius=2, thief_vision_radius=2)


def test_own_position_always_visible(board, engine):
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.own_position == (2, 2)


def test_thief_own_position_always_visible(board, engine):
    obs = engine.get_observation("thief", board, move_counter=1)
    assert obs.own_position == (4, 4)


def test_move_counter_included(board, engine):
    obs = engine.get_observation("cop", board, move_counter=7)
    assert obs.move_counter == 7


def test_barriers_always_visible(board, engine):
    board.place_barrier(1, 1)
    board.place_barrier(3, 3)
    obs = engine.get_observation("cop", board, move_counter=1)
    assert (1, 1) in obs.barriers
    assert (3, 3) in obs.barriers


def test_opponent_visible_within_radius(board, engine):
    """Cop at (2,2), Thief at (4,4) — Chebyshev=2, radius=2 → visible."""
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.opponent_pos == (4, 4)


def test_opponent_hidden_outside_radius(board, engine):
    """Move thief far away — Chebyshev > 2 → hidden."""
    board.place_agent("thief", 0, 4)  # Chebyshev from (2,2) = max(2,2)=2
    board.place_agent("thief", 0, 0)  # Chebyshev from (2,2) = max(2,2)=2
    # Put thief at distance 3
    b = GameBoard(rows=5, cols=5, max_barriers=5)
    b.place_agent("cop", 0, 0)
    b.place_agent("thief", 0, 4)  # Chebyshev = max(0,4) = 4 > 2
    obs = engine.get_observation("cop", b, move_counter=1)
    assert obs.opponent_pos is None


def test_opponent_hidden_with_zero_radius(board):
    """Vision radius 0 — cop never sees thief."""
    engine = ObservationEngine(cop_vision_radius=0, thief_vision_radius=0)
    board.place_agent("thief", 2, 3)  # Chebyshev=1, but radius=0
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.opponent_pos is None


def test_opponent_fully_visible_with_large_radius(board):
    """Vision radius 4 covers entire 5x5 board."""
    engine = ObservationEngine(cop_vision_radius=4, thief_vision_radius=4)
    board.place_agent("thief", 0, 0)  # far corner from (2,2) — Chebyshev=2
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.opponent_pos == (0, 0)


def test_last_message_included(board, engine):
    obs = engine.get_observation(
        "cop", board, move_counter=1, last_message="I see you!"
    )
    assert obs.last_message == "I see you!"


def test_last_message_none_by_default(board, engine):
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.last_message is None


def test_observation_is_dataclass(board, engine):
    obs = engine.get_observation("cop", board, move_counter=1)
    assert isinstance(obs, Observation)


def test_chebyshev_boundary_exactly_on_radius(board, engine):
    """Thief exactly at radius distance — should be visible."""
    board.place_agent("cop", 0, 0)
    board.place_agent("thief", 2, 2)  # Chebyshev = 2 == radius → visible
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.opponent_pos == (2, 2)


def test_chebyshev_boundary_one_beyond_radius(board, engine):
    """Thief one step beyond radius — should be hidden."""
    board.place_agent("cop", 0, 0)
    board.place_agent("thief", 3, 0)  # Chebyshev = 3 > 2 → hidden
    obs = engine.get_observation("cop", board, move_counter=1)
    assert obs.opponent_pos is None
