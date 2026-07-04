"""Unit tests for InfoPanel -- TDD red phase (Phase 5).

Text-formatting logic is tested directly, without a real tkinter Frame -- same
headless-renderer convention as test_board_view.py.
"""

from cop_thief.gui.game_state import GameState
from cop_thief.gui.info_panel import InfoPanel

MAX_MOVES = 25


def _state(scores=None, last_messages=None, current_turn="cop", move_counter=12):
    return GameState(
        cop_position=(0, 0),
        thief_position=(4, 4),
        barriers=[],
        move_counter=move_counter,
        sub_game_number=3,
        scores=scores or {"cop": 45, "thief": 30},
        last_messages=last_messages or {"cop": "I see you.", "thief": "No you don't."},
        current_turn=current_turn,
    )


def test_score_panel_shows_correct_scores():
    panel = InfoPanel(frame=None)
    text = panel.score_text(_state(scores={"cop": 45, "thief": 30}))
    assert "45" in text
    assert "30" in text


def test_message_panel_shows_both_agents():
    panel = InfoPanel(frame=None)
    text = panel.message_text(
        _state(last_messages={"cop": "I see you.", "thief": "No you don't."})
    )
    assert "I see you." in text
    assert "No you don't." in text


def test_turn_indicator_shows_correct_agent():
    panel = InfoPanel(frame=None)
    assert "cop" in panel.turn_text(_state(current_turn="cop")).lower()
    assert "thief" in panel.turn_text(_state(current_turn="thief")).lower()


def test_move_counter_updates():
    panel = InfoPanel(frame=None)
    text = panel.move_counter_text(_state(move_counter=12), MAX_MOVES)
    assert "12" in text
    assert str(MAX_MOVES) in text
