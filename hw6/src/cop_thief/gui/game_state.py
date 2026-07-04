"""GameState snapshot the GUI reads to render one frame -- no game logic here."""

from dataclasses import dataclass


@dataclass
class GameState:
    """One point-in-time snapshot of the game, as seen by the GUI.

    Per PRD_gui.md section 6 this is normally pushed via
    `game_session.on_state_change(callback)`, which doesn't exist yet on
    `GameSession` (Phase 1 predates the GUI). Until Phase 3's game loop wires that
    up, any caller can build a `GameState` and pass it straight to `GuiApp.update()`.
    """

    cop_position: tuple[int, int]
    thief_position: tuple[int, int]
    barriers: list[tuple[int, int]]
    move_counter: int
    sub_game_number: int
    scores: dict[str, int]
    last_messages: dict[str, str]
    current_turn: str
