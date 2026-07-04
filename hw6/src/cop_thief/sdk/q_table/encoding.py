"""Shared state/action encoding for the Cop's tactical Q-table advisor."""

from cop_thief.sdk.game_engine.board import Direction

DIRECTIONS = list(Direction)
BARRIER_ACTION = len(DIRECTIONS)  # index 8: place_barrier
NUM_ACTIONS = len(DIRECTIONS) + 1  # 8 directions + place_barrier

_DIRECTION_LABELS = {
    Direction.N: "north",
    Direction.NE: "northeast",
    Direction.E: "east",
    Direction.SE: "southeast",
    Direction.S: "south",
    Direction.SW: "southwest",
    Direction.W: "west",
    Direction.NW: "northwest",
}


def encode_state(
    cop_pos: tuple[int, int],
    thief_pos: tuple[int, int],
    rows: int,
    cols: int,
) -> int:
    """Flatten (cop_row, cop_col, thief_row, thief_col) into one Q-table row index."""
    cop_row, cop_col = cop_pos
    thief_row, thief_col = thief_pos
    return ((cop_row * cols + cop_col) * rows + thief_row) * cols + thief_col


def action_label(action_idx: int) -> str:
    """Natural-language phrase for an action index -- never raw coordinates."""
    if action_idx == BARRIER_ACTION:
        return "placing a barrier here"
    return f"moving {_DIRECTION_LABELS[DIRECTIONS[action_idx]]}"
