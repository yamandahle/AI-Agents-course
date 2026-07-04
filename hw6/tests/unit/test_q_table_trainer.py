"""Unit tests for QTableTrainer -- TDD red phase (Phase 4)."""

import numpy as np
import pytest

from cop_thief.sdk.q_table.trainer import QTableTrainer

CONFIG = dict(
    rows=3,
    cols=3,
    max_moves=10,
    max_barriers=2,
    scoring={"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5},
    alpha=0.5,
    gamma=0.9,
    epsilon=0.1,
)


@pytest.fixture
def trainer():
    return QTableTrainer(**CONFIG)


def test_q_table_initializes_to_zeros(trainer):
    assert np.all(trainer.q_table == 0.0)


def test_bellman_update_increases_good_action(trainer):
    state, action, next_state = 0, 2, 1
    trainer.update(state, action, reward=20.0, next_state=next_state, done=True)
    assert trainer.q_table[state, action] > 0.0


def test_bellman_update_decreases_bad_action(trainer):
    state, action, next_state = 0, 3, 1
    trainer.q_table[state, action] = 5.0
    trainer.update(state, action, reward=-5.0, next_state=next_state, done=True)
    assert trainer.q_table[state, action] < 5.0


def test_epsilon_greedy_explores(trainer, monkeypatch):
    module = "cop_thief.sdk.q_table.trainer.random"
    monkeypatch.setattr(f"{module}.random", lambda: 0.0)
    monkeypatch.setattr(f"{module}.choice", lambda seq: seq[0])
    action = trainer.choose_action(state=0, valid_actions=[3, 5, 7])
    assert action == 3


def test_epsilon_greedy_exploits(trainer, monkeypatch):
    trainer.q_table[0, 5] = 9.0
    monkeypatch.setattr("cop_thief.sdk.q_table.trainer.random.random", lambda: 1.0)
    action = trainer.choose_action(state=0, valid_actions=[3, 5, 7])
    assert action == 5


def test_cop_step_returns_false_when_boxed_in():
    """Regression: a Cop fully walled in by barriers must not crash the trainer."""
    boxed_in = QTableTrainer(**{**CONFIG, "max_barriers": 3})
    boxed_in._sub_game.reset((0, 0), (2, 2))
    board = boxed_in._sub_game.board
    board.place_barrier(0, 1)  # blocks E
    board.place_barrier(1, 1)  # blocks SE
    board.place_barrier(1, 0)  # blocks S -- (0,0)'s only 3 in-bounds neighbors
    assert boxed_in._cop_step() is False


def test_run_episode_stops_cleanly_when_cop_boxed_in(trainer, monkeypatch):
    """run_episode must not crash if the Cop paints itself into a corner mid-episode."""
    monkeypatch.setattr(trainer, "_valid_cop_actions", lambda: [])
    trainer._run_episode()  # must return, not raise or loop forever


def test_training_saves_npy_file(trainer, tmp_path):
    path = tmp_path / "q_table.npy"
    trainer.train(episodes=2)
    trainer.save(str(path))
    assert path.exists()
    loaded = np.load(path)
    assert loaded.shape == trainer.q_table.shape
