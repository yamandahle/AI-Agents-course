"""Unit tests for GuiApp -- TDD red phase (Phase 5). Headless path only.

Not part of TODO_phase5_gui.md's prescribed test list (it has no test file for
app.py), added because headless-mode correctness is fully testable without a
display and is worth locking in.
"""

from cop_thief.gui.app import GuiApp
from cop_thief.gui.game_state import GameState

CONFIG = {
    "grid": {"rows": 5, "cols": 5},
    "game": {"max_moves": 25},
    "gui": {
        "enabled": False,
        "cell_size_px": 80,
        "screenshot_dir": "/tmp/does-not-matter",
        "framework": "tkinter",
    },
}


def _state():
    return GameState(
        cop_position=(0, 0),
        thief_position=(4, 4),
        barriers=[],
        move_counter=0,
        sub_game_number=1,
        scores={"cop": 0, "thief": 0},
        last_messages={"cop": "", "thief": ""},
        current_turn="thief",
    )


def test_headless_mode_skips_tkinter_init():
    app = GuiApp(CONFIG, case_name="headless_test")
    assert app.root is None
    assert app.board_view is None
    assert app.info_panel is None


def test_headless_update_is_a_no_op():
    app = GuiApp(CONFIG, case_name="headless_test")
    app.update(_state())  # must not raise even with no window


def test_headless_run_in_background_is_a_no_op():
    app = GuiApp(CONFIG, case_name="headless_test")
    app.run_in_background()  # must not raise, must not start a real thread


def test_headless_close_is_a_no_op():
    app = GuiApp(CONFIG, case_name="headless_test")
    app.close()  # must not raise
