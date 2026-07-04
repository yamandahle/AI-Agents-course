"""Q-table tactical advisor: turns a trained Q-table into a natural-language hint."""

import numpy as np

from cop_thief.sdk.q_table.encoding import action_label, encode_state


class QTableAdvisor:
    """Wraps a trained Q-table and offers a one-line NL tactical hint for the Cop.

    The LLM orchestrator retains full decision authority -- this advisor only ever
    suggests, via `get_hint()`; it never picks the Cop's action itself.
    """

    def __init__(
        self,
        enabled: bool,
        q_table_path: str,
        rows: int,
        cols: int,
    ) -> None:
        """Load the trained Q-table from disk if enabled; no-op otherwise."""
        self.enabled = enabled
        self.rows = rows
        self.cols = cols
        self.q_table: np.ndarray | None = None
        if self.enabled:
            self.q_table = np.load(q_table_path)

    def get_hint(
        self,
        cop_pos: tuple[int, int],
        thief_pos: tuple[int, int],
    ) -> str:
        """Return a natural-language tactical hint, or "" if the advisor is disabled."""
        if not self.enabled or self.q_table is None:
            return ""
        state = encode_state(cop_pos, thief_pos, self.rows, self.cols)
        best_action = int(np.argmax(self.q_table[state]))
        return f"Position analysis suggests {action_label(best_action)}."
