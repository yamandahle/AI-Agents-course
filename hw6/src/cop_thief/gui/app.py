"""Main GUI app: wires BoardView + InfoPanel + ScreenshotCapture.

PRD_gui.md assumes `game_session.on_state_change(callback)`, which doesn't exist on
GameSession yet (Phase 1 predates the GUI, and Phase 3's game loop isn't built).
Rather than block on that, `GuiApp.update(state)` is the seam: any caller (a demo
script, a test, or eventually the real orchestrator) can push a GameState here.
"""

import threading
import tkinter as tk

from cop_thief.gui.board_view import BoardView
from cop_thief.gui.game_state import GameState
from cop_thief.gui.info_panel import InfoPanel
from cop_thief.gui.screenshot import ScreenshotCapture


class GuiApp:
    """Owns the tkinter window (if any) and screenshot capture for one game run.

    Fully headless when `config["gui"]["enabled"]` is false -- no tkinter object
    is created at all, so this class is always safe to instantiate even without
    a display.
    """

    def __init__(self, config: dict, case_name: str = "default") -> None:
        """Build the window (if enabled) or stay fully inert (headless)."""
        self.enabled = config["gui"]["enabled"]
        self.max_moves = config["game"]["max_moves"]
        self.screenshots = ScreenshotCapture(config["gui"]["screenshot_dir"], case_name)
        self.root: tk.Tk | None = None
        self.board_view: BoardView | None = None
        self.info_panel: InfoPanel | None = None
        if self.enabled:
            self._build_window(config)

    def update(self, state: GameState) -> None:
        """Redraw the board and info panel for the current GameState."""
        if not self.enabled:
            return
        self.board_view.render(state)
        self.info_panel.render(state, self.max_moves)
        self.root.update_idletasks()
        self.root.update()

    def run_in_background(self) -> None:
        """Start the tkinter main loop on a separate daemon thread."""
        if not self.enabled:
            return
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def close(self) -> None:
        """Close the window cleanly, if one was created."""
        if self.root is not None:
            self.root.destroy()

    def _build_window(self, config: dict) -> None:
        self.root = tk.Tk()
        self.root.title("Cop & Thief")
        rows, cols = config["grid"]["rows"], config["grid"]["cols"]
        cell_size_px = config["gui"]["cell_size_px"]

        canvas = tk.Canvas(
            self.root, width=cols * cell_size_px, height=rows * cell_size_px
        )
        canvas.pack(side="left")
        self.board_view = BoardView(canvas, rows, cols, cell_size_px)

        info_frame = tk.Frame(self.root)
        info_frame.pack(side="right", fill="y")
        self.info_panel = InfoPanel(info_frame)
