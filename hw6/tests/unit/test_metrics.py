"""Unit tests for experiment metrics collection."""

import json

from cop_thief.experiments.metrics import (
    METRIC_FIELDS,
    collect,
    save,
    write_summary_csv,
)

SAMPLE_RESULT = {
    "sub_games": [
        {"winner": "cop", "moves_played": 10, "barriers_placed": 2, "crashed": False},
        {"winner": "thief", "moves_played": 25, "barriers_placed": 1, "crashed": False},
    ],
    "totals": {"cop": 25, "thief": 15},
}

SAMPLE_CONFIG = {
    "vision": {"cop_vision_radius": 2, "thief_vision_radius": 2},
}


def test_metrics_has_all_required_fields():
    m = collect(SAMPLE_RESULT, "exp1_full_5x5", SAMPLE_CONFIG, "5x5")
    for key in METRIC_FIELDS:
        assert key in m


def test_cop_wins_count_correct():
    m = collect(SAMPLE_RESULT, "exp1_full_5x5", SAMPLE_CONFIG, "5x5")
    assert m["cop_wins"] == 1
    assert m["thief_wins"] == 1
    assert m["cop_win_rate"] == 0.5


def test_avg_capture_turn_calculated():
    m = collect(SAMPLE_RESULT, "exp1_full_5x5", SAMPLE_CONFIG, "5x5")
    assert m["avg_capture_turn"] == 10.0


def test_metrics_saved_to_json(tmp_path):
    m = collect(SAMPLE_RESULT, "exp1_full_5x5", SAMPLE_CONFIG, "5x5")
    path = save(m, tmp_path)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["case_name"] == "exp1_full_5x5"


def test_summary_csv_row_has_case_name(tmp_path):
    m = collect(SAMPLE_RESULT, "exp1_full_5x5", SAMPLE_CONFIG, "5x5")
    path = write_summary_csv([m], tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "exp1_full_5x5" in text
    assert "cop_wins" in text
