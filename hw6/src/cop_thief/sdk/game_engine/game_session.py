"""Game session: runs num_games sub-games, accumulates scores and logs."""

import logging
import random
from dataclasses import dataclass
from typing import Callable

from cop_thief.sdk.game_engine.sub_game import SubGame, SubGameResult

logger = logging.getLogger(__name__)


class TooManyCrashesError(Exception):
    """Raised when a full game exceeds its crash-retry budget."""


@dataclass
class GameResult:
    """Outcome of a full game (all sub-games + totals)."""

    sub_games: list[SubGameResult]
    totals: dict  # {"cop": int, "thief": int}

    def to_dict(self) -> dict:
        """Serialise to plain dict for Gmail JSON report."""
        return {
            "sub_games": [
                {
                    "sub_game_number": i + 1,
                    "winner": sg.winner,
                    "moves_played": sg.moves_played,
                    "cop_score": sg.cop_score,
                    "thief_score": sg.thief_score,
                    "barriers_placed": sg.barriers_placed,
                    "turns": sg.turns,
                    "crashed": sg.crashed,
                }
                for i, sg in enumerate(self.sub_games)
            ],
            "totals": self.totals,
        }


class GameSession:
    """Runs a full game of num_games valid sub-games."""

    def __init__(self, config: dict) -> None:
        """Initialise session from config dict."""
        self._cfg = config
        self._sub_game = SubGame(
            rows=config["grid"]["rows"],
            cols=config["grid"]["cols"],
            max_moves=config["game"]["max_moves"],
            max_barriers=config["game"]["max_barriers"],
            cop_vision_radius=config["vision"]["cop_vision_radius"],
            thief_vision_radius=config["vision"]["thief_vision_radius"],
            scoring=config["scoring"],
        )
        self._num_games = config["game"]["num_games"]

    def run(
        self,
        action_provider: Callable,
        fixed_starts: tuple | None = None,
    ) -> GameResult:
        """Run num_games valid sub-games using action_provider for decisions.

        action_provider(agent_id, observation) -> (Action, message: str)
        fixed_starts: optional (cop_pos, thief_pos) used for all sub-games.
        Crashed sub-games are marked and re-run until num_games valid ones exist.
        """
        results: list[SubGameResult] = []
        valid_count = 0
        max_attempts = self._num_games * 5  # safety cap against infinite crash loops

        while valid_count < self._num_games and len(results) < max_attempts:
            result = self._run_one_sub_game(action_provider, fixed_starts)
            results.append(result)
            if not result.crashed:
                valid_count += 1

        if valid_count < self._num_games:
            raise TooManyCrashesError(
                f"Only {valid_count}/{self._num_games} valid sub-games completed "
                f"after {len(results)} attempts (cap: {max_attempts})."
            )

        valid_results = [r for r in results if not r.crashed]
        totals = {
            "cop": sum(r.cop_score for r in valid_results),
            "thief": sum(r.thief_score for r in valid_results),
        }
        return GameResult(sub_games=valid_results, totals=totals)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_one_sub_game(
        self, action_provider: Callable, fixed_starts: tuple | None = None
    ) -> SubGameResult:
        """Run a single sub-game; return crashed result on any exception."""
        cop_start, thief_start = fixed_starts or self._random_starts()
        self._sub_game.reset(cop_start, thief_start)
        try:
            while not self._sub_game.is_terminal():
                self._take_turn(action_provider)
            return self._sub_game.get_result()
        except Exception as exc:
            logger.warning("sub-game crashed: %s: %s", type(exc).__name__, exc)
            return SubGameResult(
                winner="none",
                cop_score=0,
                thief_score=0,
                moves_played=self._sub_game.move_counter,
                barriers_placed=0,
                crashed=True,
            )

    def _take_turn(self, action_provider: Callable) -> None:
        """Execute one full turn: thief then cop."""
        for agent_id in ("thief", "cop"):
            obs = self._sub_game.get_observation(agent_id)
            action, message = action_provider(agent_id, obs)
            if agent_id == "thief":
                self._sub_game.apply_thief_action(action, message)
            else:
                self._sub_game.apply_cop_action(action, message)
            if self._sub_game.is_terminal():
                break

    def _random_starts(self) -> tuple:
        """Return random distinct (cop_start, thief_start) positions."""
        rows = self._cfg["grid"]["rows"]
        cols = self._cfg["grid"]["cols"]
        all_cells = [(r, c) for r in range(rows) for c in range(cols)]
        cop_start, thief_start = random.sample(all_cells, 2)
        return cop_start, thief_start
