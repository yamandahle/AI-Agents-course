"""Self-play trainer for the Cop's tactical Q-table advisor (Bellman / epsilon-greedy).

Trains the Cop only -- the action set (8 directions + place_barrier) is Cop-specific,
matching the advisor's `get_hint()` contract. The Thief opponent during self-play is a
simple random-valid-move policy; the real Thief agent doesn't exist until Phase 3.
"""

import random

import numpy as np

from cop_thief.sdk.game_engine.board import Action, InvalidMoveError
from cop_thief.sdk.game_engine.sub_game import SubGame
from cop_thief.sdk.q_table.encoding import (
    BARRIER_ACTION,
    DIRECTIONS,
    NUM_ACTIONS,
    encode_state,
)


class QTableTrainer:
    """Trains a Cop Q-table via self-play against a random Thief."""

    def __init__(
        self,
        rows: int,
        cols: int,
        max_moves: int,
        max_barriers: int,
        scoring: dict,
        alpha: float,
        gamma: float,
        epsilon: float,
    ) -> None:
        """Store training hyperparameters and initialise an empty Q-table."""
        self.rows = rows
        self.cols = cols
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.scoring = scoring
        num_states = rows * cols * rows * cols
        self.q_table = np.zeros((num_states, NUM_ACTIONS))
        self._sub_game = SubGame(
            rows=rows,
            cols=cols,
            max_moves=max_moves,
            max_barriers=max_barriers,
            cop_vision_radius=rows + cols,
            thief_vision_radius=rows + cols,
            scoring=scoring,
        )

    def choose_action(self, state: int, valid_actions: list[int]) -> int:
        """Epsilon-greedy pick among `valid_actions` (avoids illegal-move stalls)."""
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        q_values = self.q_table[state]
        return max(valid_actions, key=lambda a: q_values[a])

    def update(
        self, state: int, action: int, reward: float, next_state: int, done: bool
    ) -> None:
        """Bellman update for one (state, action, reward, next_state) transition."""
        best_next = 0.0 if done else np.max(self.q_table[next_state])
        td_target = reward + self.gamma * best_next
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error

    def train(self, episodes: int) -> None:
        """Run self-play for `episodes` episodes."""
        for _ in range(episodes):
            self._run_episode()

    def save(self, path: str) -> None:
        """Persist the trained Q-table to a .npy file."""
        np.save(path, self.q_table)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_episode(self) -> None:
        """Play one self-play sub-game: Thief moves first, then the Cop step.

        Ends early (no Q-update) if the Cop ever has zero legal actions -- e.g. its own
        barriers plus the grid edge fully box it in. The base game engine has no
        stalemate rule for this, so we just stop the episode rather than fake a legal
        move that would raise InvalidMoveError.
        """
        cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        cop_start, thief_start = random.sample(cells, 2)
        self._sub_game.reset(cop_start, thief_start)
        while not self._sub_game.is_terminal():
            self._thief_random_move()
            if self._sub_game.is_terminal():
                break
            if not self._cop_step():
                break

    def _cop_step(self) -> bool:
        """Run one Cop turn. Returns False if the Cop has no legal action at all."""
        board = self._sub_game.board
        state = encode_state(board.get_agent_pos("cop"), board.get_agent_pos("thief"),
                              self.rows, self.cols)
        valid_actions = self._valid_cop_actions()
        if not valid_actions:
            return False

        action_idx = self.choose_action(state, valid_actions)
        self._apply_cop_action(action_idx)

        done = self._sub_game.is_terminal()
        reward = self._terminal_reward() if done else 0.0
        if done:
            next_state = state
        else:
            cop_pos = board.get_agent_pos("cop")
            thief_pos = board.get_agent_pos("thief")
            next_state = encode_state(cop_pos, thief_pos, self.rows, self.cols)
        self.update(state, action_idx, reward, next_state, done)
        return True

    def _apply_cop_action(self, action_idx: int) -> None:
        direction = None if action_idx == BARRIER_ACTION else DIRECTIONS[action_idx]
        self._sub_game.apply_cop_action(Action(direction))

    def _valid_cop_actions(self) -> list[int]:
        board = self._sub_game.board
        valid = [i for i, d in enumerate(DIRECTIONS) if board.is_valid_move("cop", d)]
        if board.barriers_remaining > 0:
            valid.append(BARRIER_ACTION)
        return valid

    def _terminal_reward(self) -> float:
        result = self._sub_game.get_result()
        key = "cop_win" if result.winner == "cop" else "cop_loss"
        return float(self.scoring[key])

    def _thief_random_move(self) -> None:
        board = self._sub_game.board
        valid = [d for d in DIRECTIONS if board.is_valid_move("thief", d)]
        direction = random.choice(valid) if valid else random.choice(DIRECTIONS)
        try:
            self._sub_game.apply_thief_action(Action(direction))
        except InvalidMoveError:
            pass


def main() -> None:
    """CLI entry point: train from config.json and save to config/q_table.npy."""
    import json
    from pathlib import Path

    config_path = Path(__file__).resolve().parents[4] / "config" / "config.json"
    config = json.loads(config_path.read_text())

    trainer = QTableTrainer(
        rows=config["grid"]["rows"],
        cols=config["grid"]["cols"],
        max_moves=config["game"]["max_moves"],
        max_barriers=config["game"]["max_barriers"],
        scoring=config["scoring"],
        alpha=config["q_table"]["alpha"],
        gamma=config["q_table"]["gamma"],
        epsilon=config["q_table"]["epsilon"],
    )
    episodes = config["q_table"]["training_episodes"]
    trainer.train(episodes)
    out_path = config_path.parent / "q_table.npy"
    trainer.save(str(out_path))
    print(f"Trained {episodes} episodes -> {out_path}")


if __name__ == "__main__":
    main()
