"""Generate comparison graphs from summary.csv and per-case result logs."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _read_summary(path: Path) -> list[dict]:
    """Load summary.csv rows."""
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _case_labels(rows: list[dict]) -> list[str]:
    """Short display labels for chart axes."""
    return [f"{r['case_name']}\n({r['grid_label']})" for r in rows]


def generate_all(summary_path: Path, results_dir: Path, output_dir: Path) -> list[Path]:
    """Create all comparison charts; return saved PNG paths."""
    rows = _read_summary(summary_path)
    if not rows:
        raise ValueError(f"No rows in {summary_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = [
        _win_rates(rows, output_dir),
        _score_comparison(rows, output_dir),
        _vision_vs_winrate(rows, output_dir),
        _capture_turn_dist(results_dir, [r["case_name"] for r in rows], output_dir),
    ]
    return saved


def _win_rates(rows: list[dict], output_dir: Path) -> Path:
    """Bar chart: cop vs thief sub-game wins per experiment."""
    labels = _case_labels(rows)
    x = range(len(rows))
    width = 0.35
    cop_vals = [int(r["cop_wins"]) for r in rows]
    thief_vals = [int(r["thief_wins"]) for r in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width / 2 for i in x], cop_vals, width, label="Cop wins")
    ax.bar([i + width / 2 for i in x], thief_vals, width, label="Thief wins")
    ax.set_xticks(list(x), labels, rotation=15, ha="right")
    ax.set_ylabel("Sub-game wins")
    ax.set_title("Win counts per experiment")
    ax.legend()
    fig.tight_layout()
    path = output_dir / "win_rates.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def _score_comparison(rows: list[dict], output_dir: Path) -> Path:
    """Grouped bar chart of total scores."""
    labels = _case_labels(rows)
    x = range(len(rows))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        [i - width / 2 for i in x],
        [int(r["cop_total_score"]) for r in rows],
        width,
        label="Cop",
    )
    ax.bar(
        [i + width / 2 for i in x],
        [int(r["thief_total_score"]) for r in rows],
        width,
        label="Thief",
    )
    ax.set_xticks(list(x), labels, rotation=15, ha="right")
    ax.set_ylabel("Total score")
    ax.set_title("Total scores per experiment")
    ax.legend()
    fig.tight_layout()
    path = output_dir / "score_comparison.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def _vision_vs_winrate(rows: list[dict], output_dir: Path) -> Path:
    """Cop win rate vs cop vision radius (comparison across our 3 cases)."""
    fig, ax = plt.subplots(figsize=(7, 5))
    xs = [int(r["cop_vision"]) for r in rows]
    ys = [float(r["cop_win_rate"]) for r in rows]
    ax.plot(xs, ys, marker="o", linewidth=2)
    for r in rows:
        ax.annotate(
            r["case_name"],
            (int(r["cop_vision"]), float(r["cop_win_rate"])),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )
    ax.set_xlabel("Cop vision radius")
    ax.set_ylabel("Cop win rate")
    ax.set_title("Cop win rate vs cop vision radius")
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    path = output_dir / "vision_vs_winrate.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def _capture_turn_dist(
    results_dir: Path, case_names: list[str], output_dir: Path
) -> Path:
    """Histogram of turns when cop captured thief (all available cases)."""
    turns: list[int] = []
    for name in case_names:
        result_path = results_dir / name / "result.json"
        if not result_path.exists():
            continue
        data = json.loads(result_path.read_text(encoding="utf-8"))
        for sg in data.get("sub_games", []):
            if sg.get("winner") == "cop":
                turns.append(int(sg["moves_played"]))
    fig, ax = plt.subplots(figsize=(7, 5))
    if turns:
        ax.hist(turns, bins=max(3, min(10, len(turns))), edgecolor="black")
    ax.set_xlabel("Turn of capture")
    ax.set_ylabel("Count")
    ax.set_title("Capture turn distribution (cop wins)")
    fig.tight_layout()
    path = output_dir / "capture_turn_dist.png"
    fig.savefig(path)
    plt.close(fig)
    return path
