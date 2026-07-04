"""Integration tests for GameSession — TDD red phase."""

import pytest

from cop_thief.sdk.game_engine.board import Action, Direction
from cop_thief.sdk.game_engine.game_session import GameResult, GameSession
from cop_thief.sdk.game_engine.sub_game import SubGameResult


CONFIG = {
    "grid": {"rows": 5, "cols": 5},
    "game": {"max_moves": 25, "num_games": 3, "max_barriers": 5},
    "scoring": {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    "vision": {"cop_vision_radius": 4, "thief_vision_radius": 4},
}


def always_escape_actions():
    """Agents bounce S/N or N/S from central rows — never meet, never go OOB."""
    thief_t = [0]
    cop_t = [0]

    def provider(agent_id: str, _observation):
        if agent_id == "thief":
            thief_t[0] += 1
            d = Direction.S if thief_t[0] % 2 == 1 else Direction.N
            return Action(d), "bouncing"
        cop_t[0] += 1
        d = Direction.N if cop_t[0] % 2 == 1 else Direction.S
        return Action(d), "bouncing"

    return provider


# Fixed safe starts: cop at row 1, thief at row 3 (central cols) — bouncing never OOB
SAFE_STARTS = ((1, 1), (3, 3))


@pytest.fixture
def session():
    return GameSession(CONFIG)


def test_game_result_has_correct_num_sub_games(session):
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    assert len(result.sub_games) == CONFIG["game"]["num_games"]


def test_scores_accumulate_across_sub_games(session):
    """With thief always escaping, thief score = num_games * 10."""
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    assert result.totals["thief"] == CONFIG["game"]["num_games"] * 10
    assert result.totals["cop"] == CONFIG["game"]["num_games"] * 5


def test_game_result_is_dataclass(session):
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    assert isinstance(result, GameResult)


def test_sub_game_results_are_subgameresult(session):
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    for sg in result.sub_games:
        assert isinstance(sg, SubGameResult)


def test_crashed_sub_game_is_excluded():
    """Crashed sub-games are re-run; final count is always num_games valid ones."""
    crash_count = [0]
    thief_t = [0]
    cop_t = [0]

    def sometimes_crash(agent_id, _observation):
        if agent_id == "thief" and crash_count[0] < 2:
            crash_count[0] += 1
            raise RuntimeError("Simulated crash")
        if agent_id == "thief":
            thief_t[0] += 1
            return Action(Direction.S if thief_t[0] % 2 == 1 else Direction.N), "ok"
        cop_t[0] += 1
        return Action(Direction.N if cop_t[0] % 2 == 1 else Direction.S), "ok"

    session = GameSession(CONFIG)
    result = session.run(sometimes_crash, fixed_starts=SAFE_STARTS)
    valid = [sg for sg in result.sub_games if not sg.crashed]
    assert len(valid) == CONFIG["game"]["num_games"]


def test_sub_game_log_has_turns(session):
    """Each sub-game result contains a turn log."""
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    for sg in result.sub_games:
        assert hasattr(sg, "turns")
        assert len(sg.turns) > 0


def test_turn_log_has_required_fields(session):
    """Each turn entry contains move and message info."""
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    turn = result.sub_games[0].turns[0]
    assert "turn" in turn
    assert "thief_move" in turn
    assert "cop_move" in turn
    assert "thief_message" in turn
    assert "cop_message" in turn


def test_game_result_to_dict(session):
    """GameResult serialises to dict with all required Gmail report fields."""
    result = session.run(always_escape_actions(), fixed_starts=SAFE_STARTS)
    d = result.to_dict()
    assert "sub_games" in d
    assert "totals" in d
    assert "cop" in d["totals"]
    assert "thief" in d["totals"]
