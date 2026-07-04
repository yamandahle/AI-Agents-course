"""Builds GUI-facing GameState snapshots from the live game loop's state."""

from cop_thief.gui.game_state import GameState
from cop_thief.sdk.game_engine.sub_game import SubGame


def build_game_state(
    sub_game: SubGame,
    sub_game_number: int,
    totals: dict,
    last_messages: dict,
    current_turn: str,
) -> GameState:
    """Snapshot the sub_game's true (non-fog-of-war) state for the GUI."""
    board = sub_game.board
    return GameState(
        cop_position=board.get_agent_pos("cop"),
        thief_position=board.get_agent_pos("thief"),
        barriers=board.get_all_barriers(),
        move_counter=sub_game.move_counter,
        sub_game_number=sub_game_number,
        scores=dict(totals),
        last_messages=dict(last_messages),
        current_turn=current_turn,
    )
