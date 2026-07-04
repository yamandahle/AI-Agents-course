"""Sub-game: one pursuit episode (max N turns, thief moves first)."""

from dataclasses import dataclass

from cop_thief.sdk.game_engine.board import Action, GameBoard
from cop_thief.sdk.game_engine.observation import Observation, ObservationEngine


@dataclass
class SubGameResult:
    """Outcome of a single sub-game."""

    winner: str          # "cop" or "thief"
    cop_score: int
    thief_score: int
    moves_played: int
    barriers_placed: int
    turns: list = None   # turn-by-turn log dicts
    crashed: bool = False

    def __post_init__(self):
        """Default turns to empty list."""
        if self.turns is None:
            self.turns = []


class SubGame:
    """Manages one sub-game: turn order, win detection, score calculation."""

    def __init__(
        self,
        rows: int,
        cols: int,
        max_moves: int,
        max_barriers: int,
        cop_vision_radius: int,
        thief_vision_radius: int,
        scoring: dict,
    ) -> None:
        """Initialise sub-game with config values."""
        self._rows = rows
        self._cols = cols
        self._max_moves = max_moves
        self._max_barriers = max_barriers
        self._scoring = scoring
        self._obs_engine = ObservationEngine(cop_vision_radius, thief_vision_radius)
        self.board: GameBoard | None = None
        self._move_counter = 0
        self._winner: str | None = None
        self._thief_moved_this_turn = False
        self._turns: list[dict] = []
        self._current_turn: dict = {}

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def reset(
        self,
        cop_start: tuple[int, int],
        thief_start: tuple[int, int],
    ) -> None:
        """Reset board and counters for a new sub-game."""
        self.board = GameBoard(self._rows, self._cols, self._max_barriers)
        self.board.place_agent("cop", *cop_start)
        self.board.place_agent("thief", *thief_start)
        self._move_counter = 0
        self._winner = None
        self._thief_moved_this_turn = False
        self._turns = []
        self._current_turn = {}

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def apply_thief_action(
        self, action: Action, message: str = ""
    ) -> None:
        """Apply thief's move. Must be called before cop's action each turn."""
        self.board.move_agent("thief", action.direction)
        self._thief_moved_this_turn = True
        self._current_turn = {
            "turn": self._move_counter + 1,
            "thief_move": action.direction.name if action.direction else "BARRIER",
            "thief_message": message,
            "cop_move": None,
            "cop_message": "",
        }

    def apply_cop_action(
        self, action: Action, message: str = ""
    ) -> None:
        """Apply cop's move or barrier. Detects capture and turn-end survival."""
        if action.direction is None:
            cop_pos = self.board.get_agent_pos("cop")
            self.board.place_barrier(*cop_pos)
            move_name = "BARRIER"
        else:
            self.board.move_agent("cop", action.direction)
            move_name = action.direction.name
            if self.board.get_agent_pos("cop") == self.board.get_agent_pos("thief"):
                self._winner = "cop"

        self._current_turn["cop_move"] = move_name
        self._current_turn["cop_message"] = message
        self._turns.append(self._current_turn)
        self._current_turn = {}
        self._move_counter += 1
        self._thief_moved_this_turn = False

        if self._winner is None and self._move_counter >= self._max_moves:
            self._winner = "thief"

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_terminal(self) -> bool:
        """Return True when the sub-game has ended."""
        return self._winner is not None

    @property
    def move_counter(self) -> int:
        """Number of completed full turns."""
        return self._move_counter

    def get_observation(
        self,
        agent_id: str,
        last_message: str | None = None,
    ) -> Observation:
        """Return fog-of-war observation for agent."""
        return self._obs_engine.get_observation(
            agent_id, self.board, self._move_counter, last_message
        )

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    def get_result(self) -> SubGameResult:
        """Return sub-game result. Raises RuntimeError if game not over."""
        if not self.is_terminal():
            raise RuntimeError("Sub-game is not finished yet.")
        if self._winner == "cop":
            cop_score = self._scoring["cop_win"]
            thief_score = self._scoring["thief_loss"]
        else:
            cop_score = self._scoring["cop_loss"]
            thief_score = self._scoring["thief_win"]
        return SubGameResult(
            winner=self._winner,
            cop_score=cop_score,
            thief_score=thief_score,
            moves_played=self._move_counter,
            barriers_placed=self._max_barriers - self.board.barriers_remaining,
            turns=list(self._turns),
        )
