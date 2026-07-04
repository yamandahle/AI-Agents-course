"""Unit tests for GameBoard — written before implementation (TDD red phase)."""

import pytest

from cop_thief.sdk.game_engine.board import (
    Action,
    Direction,
    GameBoard,
    InvalidMoveError,
    BarrierLimitError,
)


@pytest.fixture
def board():
    """5x5 board with cop at (0,0) and thief at (4,4)."""
    b = GameBoard(rows=5, cols=5, max_barriers=5)
    b.place_agent("cop", 0, 0)
    b.place_agent("thief", 4, 4)
    return b


def test_move_north(board):
    board.place_agent("cop", 2, 2)
    board.move_agent("cop", Direction.N)
    assert board.get_agent_pos("cop") == (1, 2)


def test_move_northeast(board):
    board.place_agent("cop", 2, 2)
    board.move_agent("cop", Direction.NE)
    assert board.get_agent_pos("cop") == (1, 3)


def test_move_all_8_directions(board):
    """Each direction moves agent by the correct delta."""
    expected = {
        Direction.N:  (-1,  0),
        Direction.NE: (-1,  1),
        Direction.E:  ( 0,  1),
        Direction.SE: ( 1,  1),
        Direction.S:  ( 1,  0),
        Direction.SW: ( 1, -1),
        Direction.W:  ( 0, -1),
        Direction.NW: (-1, -1),
    }
    for direction, (dr, dc) in expected.items():
        b = GameBoard(rows=5, cols=5, max_barriers=5)
        b.place_agent("cop", 2, 2)
        b.move_agent("cop", direction)
        assert b.get_agent_pos("cop") == (2 + dr, 2 + dc)


def test_move_out_of_bounds_raises(board):
    board.place_agent("cop", 0, 0)
    with pytest.raises(InvalidMoveError):
        board.move_agent("cop", Direction.N)


def test_move_blocked_by_barrier_raises(board):
    board.place_agent("cop", 2, 2)
    board.place_barrier(1, 2)
    with pytest.raises(InvalidMoveError):
        board.move_agent("cop", Direction.N)


def test_place_barrier_on_empty_cell(board):
    board.place_barrier(1, 1)
    assert board.is_barrier(1, 1)


def test_place_barrier_decrements_remaining(board):
    board.place_barrier(1, 1)
    assert board.barriers_remaining == 4


def test_barrier_limit_raises(board):
    for r in range(5):
        board.place_barrier(r, 1)
    with pytest.raises(BarrierLimitError):
        board.place_barrier(0, 2)


def test_get_all_barriers(board):
    board.place_barrier(1, 1)
    board.place_barrier(2, 2)
    assert (1, 1) in board.get_all_barriers()
    assert (2, 2) in board.get_all_barriers()


def test_chebyshev_distance_same_cell():
    b = GameBoard(rows=5, cols=5, max_barriers=5)
    assert b.chebyshev((2, 2), (2, 2)) == 0


def test_chebyshev_distance_diagonal():
    b = GameBoard(rows=5, cols=5, max_barriers=5)
    assert b.chebyshev((0, 0), (2, 2)) == 2


def test_chebyshev_distance_straight():
    b = GameBoard(rows=5, cols=5, max_barriers=5)
    assert b.chebyshev((0, 0), (0, 3)) == 3


def test_to_dict_has_required_keys(board):
    d = board.to_dict()
    assert "cop_pos" in d
    assert "thief_pos" in d
    assert "barriers" in d
    assert "rows" in d
    assert "cols" in d
