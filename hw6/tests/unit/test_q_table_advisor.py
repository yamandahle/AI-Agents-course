"""Unit tests for QTableAdvisor -- TDD red phase (Phase 4)."""

import numpy as np
import pytest

from cop_thief.sdk.q_table.advisor import QTableAdvisor
from cop_thief.sdk.q_table.encoding import NUM_ACTIONS, encode_state

ROWS, COLS = 2, 2
NUM_STATES = ROWS * COLS * ROWS * COLS


@pytest.fixture
def q_table_path(tmp_path):
    """A tiny trained Q-table where East (action 2) is the best move for one state."""
    path = tmp_path / "q_table.npy"
    table = np.zeros((NUM_STATES, NUM_ACTIONS))
    state = encode_state((0, 0), (1, 1), ROWS, COLS)
    table[state, 2] = 5.0  # action index 2 == Direction.E
    np.save(path, table)
    return str(path)


def _advisor(q_table_path, enabled=True):
    return QTableAdvisor(
        enabled=enabled, q_table_path=q_table_path, rows=ROWS, cols=COLS
    )


def test_hint_returns_string(q_table_path):
    hint = _advisor(q_table_path).get_hint((0, 0), (1, 1))
    assert isinstance(hint, str)
    assert hint != ""


def test_hint_is_natural_language_not_coords(q_table_path):
    hint = _advisor(q_table_path).get_hint((0, 0), (1, 1))
    assert "(" not in hint
    assert not any(ch.isdigit() for ch in hint)


def test_hint_matches_best_q_action(q_table_path):
    hint = _advisor(q_table_path).get_hint((0, 0), (1, 1))
    assert "east" in hint.lower()


def test_hint_empty_when_disabled(q_table_path):
    advisor = _advisor(q_table_path, enabled=False)
    assert advisor.get_hint((0, 0), (1, 1)) == ""


def test_loads_npy_file_on_init(q_table_path):
    advisor = _advisor(q_table_path)
    assert advisor.q_table is not None
    assert advisor.q_table.shape == (NUM_STATES, NUM_ACTIONS)
