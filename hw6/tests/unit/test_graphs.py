"""Unit tests for experiment graph generation."""

import csv
import json

from cop_thief.experiments.graphs import generate_all


def _write_summary(path, rows):
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _sample_rows():
    return [
        {
            "case_name": "exp1_full_5x5",
            "grid_label": "5x5",
            "cop_vision": "2",
            "thief_vision": "2",
            "cop_wins": "4",
            "thief_wins": "2",
            "cop_win_rate": "0.667",
            "cop_total_score": "90",
            "thief_total_score": "40",
        },
        {
            "case_name": "exp2_small_blind_cop",
            "grid_label": "3x2",
            "cop_vision": "0",
            "thief_vision": "2",
            "cop_wins": "1",
            "thief_wins": "1",
            "cop_win_rate": "0.5",
            "cop_total_score": "25",
            "thief_total_score": "15",
        },
    ]


def test_win_rate_chart_saved(tmp_path):
    summary = tmp_path / "summary.csv"
    _write_summary(summary, _sample_rows())
    (tmp_path / "exp1_full_5x5").mkdir()
    (tmp_path / "exp1_full_5x5" / "result.json").write_text(
        json.dumps({"sub_games": [{"winner": "cop", "moves_played": 5}]}),
        encoding="utf-8",
    )
    out = tmp_path / "graphs"
    paths = generate_all(summary, tmp_path, out)
    assert (out / "win_rates.png").exists()
    assert len(paths) == 4


def test_charts_saved_to_correct_dir(tmp_path):
    summary = tmp_path / "summary.csv"
    _write_summary(summary, _sample_rows())
    out = tmp_path / "graphs"
    generate_all(summary, tmp_path, out)
    for name in (
        "win_rates.png",
        "score_comparison.png",
        "vision_vs_winrate.png",
        "capture_turn_dist.png",
    ):
        assert (out / name).exists()
