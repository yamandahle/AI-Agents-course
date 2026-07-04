"""Collect and persist per-case experiment metrics."""

import csv
import json
from pathlib import Path

METRIC_FIELDS = [
    "case_name",
    "grid_label",
    "cop_vision",
    "thief_vision",
    "num_sub_games",
    "cop_wins",
    "thief_wins",
    "cop_win_rate",
    "cop_total_score",
    "thief_total_score",
    "avg_capture_turn",
    "avg_moves_per_subgame",
    "barriers_used_avg",
]


def collect(result: dict, case_name: str, config: dict, grid_label: str) -> dict:
    """Build a metrics dict from a game result and its config."""
    sub_games = [sg for sg in result["sub_games"] if not sg.get("crashed")]
    cop_wins = sum(1 for sg in sub_games if sg["winner"] == "cop")
    thief_wins = sum(1 for sg in sub_games if sg["winner"] == "thief")
    n = len(sub_games) or 1
    capture_turns = [sg["moves_played"] for sg in sub_games if sg["winner"] == "cop"]
    return {
        "case_name": case_name,
        "grid_label": grid_label,
        "cop_vision": config["vision"]["cop_vision_radius"],
        "thief_vision": config["vision"]["thief_vision_radius"],
        "num_sub_games": len(sub_games),
        "cop_wins": cop_wins,
        "thief_wins": thief_wins,
        "cop_win_rate": round(cop_wins / n, 3),
        "cop_total_score": result["totals"]["cop"],
        "thief_total_score": result["totals"]["thief"],
        "avg_capture_turn": round(sum(capture_turns) / len(capture_turns), 2)
        if capture_turns
        else 0.0,
        "avg_moves_per_subgame": round(
            sum(sg["moves_played"] for sg in sub_games) / n, 2
        ),
        "barriers_used_avg": round(
            sum(sg.get("barriers_placed", 0) for sg in sub_games) / n, 2
        ),
    }


def save(metrics: dict, results_dir: Path) -> Path:
    """Write metrics.json for one case."""
    out_dir = results_dir / metrics["case_name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "metrics.json"
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return path


def write_summary_csv(all_metrics: list[dict], results_dir: Path) -> Path:
    """Overwrite results/summary.csv with one row per case."""
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / "summary.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=METRIC_FIELDS)
        writer.writeheader()
        writer.writerows(all_metrics)
    return path
