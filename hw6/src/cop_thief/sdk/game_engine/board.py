"""Game board: grid state, agent positions, barrier management, movement."""

from dataclasses import dataclass
from enum import Enum


class InvalidMoveError(Exception):
    """Raised when an agent attempts an illegal move."""


class BarrierLimitError(Exception):
    """Raised when cop tries to place more barriers than allowed."""


class Direction(Enum):
    """Eight movement directions with (row_delta, col_delta)."""

    N  = (-1,  0)
    NE = (-1,  1)
    E  = ( 0,  1)
    SE = ( 1,  1)
    S  = ( 1,  0)
    SW = ( 1, -1)
    W  = ( 0, -1)
    NW = (-1, -1)


@dataclass
class Action:
    """An agent action: either a move direction or a barrier placement."""

    direction: Direction | None = None  # None means place_barrier


class GameBoard:
    """2-D grid tracking agent positions and placed barriers."""

    def __init__(self, rows: int, cols: int, max_barriers: int) -> None:
        """Initialise an empty board with given dimensions."""
        self.rows = rows
        self.cols = cols
        self.max_barriers = max_barriers
        self._positions: dict[str, tuple[int, int]] = {}
        self._barriers: set[tuple[int, int]] = set()

    # ------------------------------------------------------------------
    # Agent placement
    # ------------------------------------------------------------------

    def place_agent(self, agent_id: str, row: int, col: int) -> None:
        """Set agent's starting position (no validation — setup only)."""
        self._positions[agent_id] = (row, col)

    def get_agent_pos(self, agent_id: str) -> tuple[int, int]:
        """Return current (row, col) for agent."""
        return self._positions[agent_id]

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move_agent(self, agent_id: str, direction: Direction) -> None:
        """Move agent one cell in direction; raise InvalidMoveError if illegal."""
        r, c = self._positions[agent_id]
        dr, dc = direction.value
        nr, nc = r + dr, c + dc
        if not self._in_bounds(nr, nc):
            raise InvalidMoveError(f"({nr},{nc}) is out of bounds.")
        if (nr, nc) in self._barriers:
            raise InvalidMoveError(f"({nr},{nc}) is a barrier.")
        self._positions[agent_id] = (nr, nc)

    def is_valid_move(self, agent_id: str, direction: Direction) -> bool:
        """Return True if the move is legal without raising."""
        r, c = self._positions[agent_id]
        dr, dc = direction.value
        nr, nc = r + dr, c + dc
        return self._in_bounds(nr, nc) and (nr, nc) not in self._barriers

    # ------------------------------------------------------------------
    # Barriers
    # ------------------------------------------------------------------

    def place_barrier(self, row: int, col: int) -> None:
        """Place barrier at (row, col); raise BarrierLimitError if at cap."""
        if len(self._barriers) >= self.max_barriers:
            raise BarrierLimitError("Maximum barriers already placed.")
        self._barriers.add((row, col))

    def is_barrier(self, row: int, col: int) -> bool:
        """Return True if cell contains a barrier."""
        return (row, col) in self._barriers

    def get_all_barriers(self) -> list[tuple[int, int]]:
        """Return sorted list of all barrier positions."""
        return sorted(self._barriers)

    @property
    def barriers_remaining(self) -> int:
        """Number of barriers the cop can still place."""
        return self.max_barriers - len(self._barriers)

    # ------------------------------------------------------------------
    # Distance
    # ------------------------------------------------------------------

    @staticmethod
    def chebyshev(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        """Chebyshev (chessboard) distance between two cells."""
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise board state to a plain dict."""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "cop_pos": self._positions.get("cop"),
            "thief_pos": self._positions.get("thief"),
            "barriers": self.get_all_barriers(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols
