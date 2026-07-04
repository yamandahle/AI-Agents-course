"""Unit tests for BoardView -- TDD red phase (Phase 5).

Cell-color logic is tested directly, without a real tkinter Canvas -- per this
project's own GUI test convention ("headless renderer, no real window in CI").
"""

from cop_thief.gui.board_view import (
    BARRIER_COLOR,
    COP_COLOR,
    EMPTY_COLOR,
    THIEF_COLOR,
    BoardView,
)
from cop_thief.gui.game_state import GameState

ROWS, COLS, CELL_PX = 5, 5, 80


def _state(cop_position=(0, 0), thief_position=(4, 4), barriers=None):
    return GameState(
        cop_position=cop_position,
        thief_position=thief_position,
        barriers=barriers or [],
        move_counter=0,
        sub_game_number=1,
        scores={"cop": 0, "thief": 0},
        last_messages={"cop": "", "thief": ""},
        current_turn="thief",
    )


def _view():
    return BoardView(canvas=None, rows=ROWS, cols=COLS, cell_size_px=CELL_PX)


def test_cop_cell_colored_blue():
    view = _view()
    state = _state(cop_position=(2, 3))
    assert view.cell_color(2, 3, state) == COP_COLOR


def test_thief_cell_colored_red():
    view = _view()
    state = _state(thief_position=(1, 1))
    assert view.cell_color(1, 1, state) == THIEF_COLOR


def test_barrier_cell_colored_gray():
    view = _view()
    state = _state(barriers=[(3, 3)])
    assert view.cell_color(3, 3, state) == BARRIER_COLOR


def test_empty_cell_colored_white():
    view = _view()
    state = _state(cop_position=(0, 0), thief_position=(4, 4), barriers=[(3, 3)])
    assert view.cell_color(2, 2, state) == EMPTY_COLOR


def test_board_dimensions_match_config():
    view = BoardView(canvas=None, rows=ROWS, cols=COLS, cell_size_px=CELL_PX)
    assert view.canvas_width_px() == COLS * CELL_PX
    assert view.canvas_height_px() == ROWS * CELL_PX
