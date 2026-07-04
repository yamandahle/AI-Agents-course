"""Tkinter Canvas grid renderer -- draws Cop, Thief, barriers, empty cells."""

import tkinter as tk

from cop_thief.gui.game_state import GameState

COP_COLOR = "blue"
THIEF_COLOR = "red"
BARRIER_COLOR = "gray"
EMPTY_COLOR = "white"


class BoardView:
    """Renders a GameState onto a tkinter Canvas.

    `cell_color()` is pure logic (no tkinter dependency) so it's directly unit
    testable without a display; `render()` is the only method that touches the
    real Canvas, and is only exercised when actually running the app.
    """

    def __init__(
        self, canvas: tk.Canvas | None, rows: int, cols: int, cell_size_px: int
    ) -> None:
        """Store the target canvas (may be None for pure-logic use) and geometry."""
        self.canvas = canvas
        self.rows = rows
        self.cols = cols
        self.cell_size_px = cell_size_px

    def cell_color(self, row: int, col: int, state: GameState) -> str:
        """Return the fill color for one cell given the current GameState."""
        if (row, col) == tuple(state.cop_position):
            return COP_COLOR
        if (row, col) == tuple(state.thief_position):
            return THIEF_COLOR
        if (row, col) in state.barriers:
            return BARRIER_COLOR
        return EMPTY_COLOR

    def canvas_width_px(self) -> int:
        """Total canvas width for this grid, in pixels."""
        return self.cols * self.cell_size_px

    def canvas_height_px(self) -> int:
        """Total canvas height for this grid, in pixels."""
        return self.rows * self.cell_size_px

    def render(self, state: GameState) -> None:
        """Redraw the full grid on the real canvas for the given GameState."""
        self.canvas.delete("all")
        size = self.cell_size_px
        for row in range(self.rows):
            for col in range(self.cols):
                x0, y0 = col * size, row * size
                color = self.cell_color(row, col, state)
                self.canvas.create_rectangle(
                    x0, y0, x0 + size, y0 + size, fill=color, outline="black"
                )
