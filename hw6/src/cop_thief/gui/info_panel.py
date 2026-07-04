"""Tkinter info panel: scores, messages, turn indicator, move counter."""

import tkinter as tk

from cop_thief.gui.game_state import GameState


class InfoPanel:
    """Renders score/message/turn/move-counter text from a GameState.

    Text-formatting methods are pure logic (no tkinter dependency); `render()` is
    the only method that touches real widgets, and is only exercised when
    actually running the app -- same split as BoardView.
    """

    def __init__(self, frame: tk.Frame | None) -> None:
        """Store the parent frame (None is fine for pure-logic use/tests)."""
        self.frame = frame
        self._score_label: tk.Label | None = None
        self._message_label: tk.Label | None = None
        self._turn_label: tk.Label | None = None
        self._move_label: tk.Label | None = None

    def score_text(self, state: GameState) -> str:
        """Return the score line, e.g. 'Cop: 45   Thief: 30'."""
        return f"Cop: {state.scores['cop']}   Thief: {state.scores['thief']}"

    def message_text(self, state: GameState) -> str:
        """Return both agents' last messages as a two-line string."""
        cop_msg = state.last_messages.get("cop") or ""
        thief_msg = state.last_messages.get("thief") or ""
        return f'Cop: "{cop_msg}"\nThief: "{thief_msg}"'

    def turn_text(self, state: GameState) -> str:
        """Return whose turn it is, e.g. 'Cop turn'."""
        return f"{state.current_turn.capitalize()} turn"

    def move_counter_text(self, state: GameState, max_moves: int) -> str:
        """Return the move counter, e.g. 'Move: 12/25'."""
        return f"Move: {state.move_counter}/{max_moves}"

    def render(self, state: GameState, max_moves: int) -> None:
        """Update the real tkinter labels, creating them on first use."""
        if self.frame is None:
            return
        if self._score_label is None:
            self._score_label = tk.Label(self.frame)
            self._message_label = tk.Label(self.frame, justify="left")
            self._turn_label = tk.Label(self.frame)
            self._move_label = tk.Label(self.frame)
            for label in (
                self._score_label,
                self._message_label,
                self._turn_label,
                self._move_label,
            ):
                label.pack(anchor="w")
        self._score_label.config(text=self.score_text(state))
        self._message_label.config(text=self.message_text(state))
        self._turn_label.config(text=self.turn_text(state))
        self._move_label.config(text=self.move_counter_text(state, max_moves))
