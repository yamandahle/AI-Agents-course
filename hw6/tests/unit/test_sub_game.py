"""Unit tests for SubGame — TDD red phase."""

import pytest

from cop_thief.sdk.game_engine.board import Direction, Action, InvalidMoveError
from cop_thief.sdk.game_engine.sub_game import SubGame, SubGameResult


@pytest.fixture
def game():
    """SubGame with 5x5 board, max 5 moves, max 5 barriers, scoring from defaults."""
    return SubGame(
        rows=5, cols=5,
        max_moves=5,
        max_barriers=5,
        cop_vision_radius=4,
        thief_vision_radius=4,
        scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    )


def test_cop_wins_by_capture():
    """Cop steps onto thief's cell → cop wins."""
    g = SubGame(
        rows=5, cols=5, max_moves=25, max_barriers=5,
        cop_vision_radius=4, thief_vision_radius=4,
        scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    )
    # Cop at (1,1), thief at (1,3) → thief moves W to (1,2), cop moves E to (1,2) → CAPTURE
    g.reset(cop_start=(1, 1), thief_start=(1, 3))
    g.apply_thief_action(Action(Direction.W))  # thief → (1,2)
    g.apply_cop_action(Action(Direction.E))    # cop → (1,2) — CAPTURE
    assert g.is_terminal()
    assert g.get_result().winner == "cop"


def test_cop_wins_result_scores():
    """Cop-win sub-game gives correct scores."""
    g = SubGame(
        rows=5, cols=5, max_moves=25, max_barriers=5,
        cop_vision_radius=4, thief_vision_radius=4,
        scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    )
    g.reset(cop_start=(1, 1), thief_start=(1, 2))
    g.apply_thief_action(Action(Direction.S))  # thief → (2,2)
    g.apply_cop_action(Action(Direction.SE))   # cop → (2,2) — CAPTURE
    result = g.get_result()
    assert result.cop_score == 20
    assert result.thief_score == 5


def test_thief_wins_by_survival():
    """Thief survives max_moves turns → thief wins."""
    g = SubGame(
        rows=5, cols=5, max_moves=3, max_barriers=5,
        cop_vision_radius=4, thief_vision_radius=4,
        scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    )
    g.reset(cop_start=(0, 0), thief_start=(4, 4))
    for _ in range(3):
        g.apply_thief_action(Action(Direction.N))
        if not g.is_terminal():
            g.apply_cop_action(Action(Direction.SE))
    assert g.is_terminal()
    assert g.get_result().winner == "thief"


def test_thief_wins_result_scores():
    """Thief-win sub-game gives correct scores."""
    g = SubGame(
        rows=5, cols=5, max_moves=2, max_barriers=5,
        cop_vision_radius=4, thief_vision_radius=4,
        scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    )
    g.reset(cop_start=(0, 0), thief_start=(4, 4))
    for _ in range(2):
        g.apply_thief_action(Action(Direction.N))
        if not g.is_terminal():
            g.apply_cop_action(Action(Direction.S))
    result = g.get_result()
    assert result.thief_score == 10
    assert result.cop_score == 5


def test_move_counter_increments(game):
    """Move counter increases after each full turn."""
    game.reset(cop_start=(0, 0), thief_start=(4, 4))
    assert game.move_counter == 0
    game.apply_thief_action(Action(Direction.N))
    game.apply_cop_action(Action(Direction.S))
    assert game.move_counter == 1


def test_invalid_move_raises(game):
    """Moving out of bounds raises InvalidMoveError."""
    game.reset(cop_start=(0, 0), thief_start=(0, 4))
    # thief at (0,4) moving N → (-1,4) out of bounds
    with pytest.raises(InvalidMoveError):
        game.apply_thief_action(Action(Direction.N))
    # cop at (0,0) moving W → (0,-1) out of bounds
    with pytest.raises(InvalidMoveError):
        game.apply_cop_action(Action(Direction.W))


def test_cop_place_barrier(game):
    """Cop can place barrier on current cell."""
    game.reset(cop_start=(2, 2), thief_start=(4, 4))
    game.apply_thief_action(Action(Direction.N))
    game.apply_cop_action(Action(direction=None))  # place barrier
    assert game.board.is_barrier(2, 2)


def test_not_terminal_at_start(game):
    """Sub-game is not terminal before any moves."""
    game.reset(cop_start=(0, 0), thief_start=(4, 4))
    assert not game.is_terminal()


def test_get_result_raises_before_terminal(game):
    """Calling get_result before game ends raises RuntimeError."""
    game.reset(cop_start=(0, 0), thief_start=(4, 4))
    with pytest.raises(RuntimeError):
        game.get_result()


def test_observation_fog_of_war(game):
    """With radius 0, opponent not visible."""
    g = SubGame(
        rows=5, cols=5, max_moves=25, max_barriers=5,
        cop_vision_radius=0, thief_vision_radius=0,
        scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    )
    g.reset(cop_start=(0, 0), thief_start=(4, 4))
    obs = g.get_observation("cop")
    assert obs.opponent_pos is None
