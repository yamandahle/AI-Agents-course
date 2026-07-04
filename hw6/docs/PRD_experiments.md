# PRD — Experiments

**Mechanism:** Experiment Runner & Analysis  
**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft

---

## 1. Purpose

Run the game under a set of named configurations to study how vision radius,
Q-table assistance, thief communication style, and starting distance affect
outcome. All experiments are config-driven — zero code changes between runs.
Results, graphs, and screenshots are saved automatically.

---

## 2. Experiment Dimensions

| Dimension | Config key | Values tested |
|-----------|-----------|---------------|
| Cop vision radius | `vision.cop_vision_radius` | 0, 1, 2, 4 |
| Thief vision radius | `vision.thief_vision_radius` | 0, 1, 2, 4 |
| Q-table advisor | `q_table.enabled` | true, false |
| Thief prompt style | `experiments.thief_style` | honest, vague, deceptive |
| Initial placement | `experiments.placement` | random, max_distance |

---

## 3. Experiment Cases

| Case | cop_vision | thief_vision | q_table | thief_style | placement | Hypothesis |
|------|-----------|--------------|---------|-------------|-----------|-----------|
| A — Baseline | 2 | 2 | off | honest | random | Balanced ~50/50 |
| B — Blind Cop | 0 | 2 | off | honest | random | Thief dominates |
| C — Full Vision | 4 | 4 | off | honest | random | Cop dominates |
| D — RL Cop | 2 | 2 | on | honest | random | Q-table raises cop win rate vs Case A |
| E — Deceptive Thief | 2 | 2 | off | deceptive | random | Deception helps Thief survive longer |
| F — Close Start | 2 | 2 | off | honest | close | Cop wins faster (fewer moves per win) |
| G — Max Distance | 2 | 2 | off | honest | max_distance | Thief wins more often |

Each case = 1 full game (6 sub-games). Total: 7 games × 6 sub-games = 42 sub-games.

---

## 4. Config Overlay System

Each experiment case overrides the base `config.json` with a small patch dict.
No code changes, no duplicate config files.

```python
EXPERIMENT_CASES = {
    "A_baseline":      {"vision": {"cop_vision_radius": 2, "thief_vision_radius": 2},
                        "q_table": {"enabled": False},
                        "experiments": {"thief_style": "honest", "placement": "random"}},
    "B_blind_cop":     {"vision": {"cop_vision_radius": 0, "thief_vision_radius": 2}, ...},
    "C_full_vision":   {"vision": {"cop_vision_radius": 4, "thief_vision_radius": 4}, ...},
    "D_rl_cop":        {"q_table": {"enabled": True}, ...},
    "E_deceptive":     {"experiments": {"thief_style": "deceptive"}, ...},
    "F_close_start":   {"experiments": {"placement": "close"}, ...},
    "G_max_distance":  {"experiments": {"placement": "max_distance"}, ...},
}
```

---

## 5. Metrics Collected Per Case

| Metric | Description |
|--------|-------------|
| `cop_wins` | Number of sub-games won by Cop |
| `thief_wins` | Number of sub-games won by Thief |
| `cop_total_score` | Cumulative Cop score across 6 sub-games |
| `thief_total_score` | Cumulative Thief score across 6 sub-games |
| `avg_capture_turn` | Average turn number when Cop captured Thief (cop_wins only) |
| `avg_moves_per_subgame` | Average moves played per sub-game |
| `barriers_used_avg` | Average barriers placed by Cop per sub-game |
| `messages_per_subgame` | Total messages exchanged per sub-game |

Saved to `results/<case_name>/metrics.json` after each case.

---

## 6. Outputs

### Per case
- `results/<case_name>/metrics.json` — raw metrics
- `results/<case_name>/game_log.json` — full move-by-move log
- `results/<case_name>/messages.txt` — all agent messages
- `assets/screenshots/<case_name>/` — screenshots at key moments:
  - `sg<N>_start.png` — board at sub-game start
  - `sg<N>_barrier.png` — first barrier placed
  - `sg<N>_capture.png` — cop captures thief (if applicable)
  - `sg<N>_escape.png` — thief escapes 25 moves (if applicable)
  - `final_score.png` — scoreboard after 6 sub-games

### Aggregate (all cases)
- `results/summary.csv` — one row per case, all metrics
- Graphs (saved to `results/graphs/`):
  - `win_rates.png` — cop vs thief win rate bar chart per case
  - `score_comparison.png` — total scores per case
  - `capture_turn_dist.png` — histogram of capture turns (cases A, C, D)
  - `vision_vs_winrate.png` — line plot: cop win rate vs cop_vision_radius
  - `rl_impact.png` — cop win rate with and without Q-table (cases A vs D)

---

## 7. Screenshot Automation

Screenshots captured via `PIL.ImageGrab` triggered by game engine events.
The GUI must be running (set `gui.enabled = true` during experiments).

```python
class ScreenshotCapture:
    def on_subgame_start(self, case_name, sg_num): ...
    def on_barrier_placed(self, case_name, sg_num): ...
    def on_cop_wins(self, case_name, sg_num): ...
    def on_thief_wins(self, case_name, sg_num): ...
    def on_game_end(self, case_name): ...
```

---

## 8. Notebook

`notebooks/experiments.ipynb` contains:
1. Load `results/summary.csv`
2. Reproduce all graphs with `matplotlib` / `seaborn`
3. Written analysis per case: did the hypothesis hold?
4. Conclusion: which configuration favors Cop, which favors Thief, and why
5. Display inline screenshots for key moments

---

## 9. How to Run

```bash
# Run all experiment cases sequentially
uv run python -m cop_thief.experiments.runner --all

# Run a single case
uv run python -m cop_thief.experiments.runner --case D_rl_cop

# Open results notebook
uv run jupyter notebook notebooks/experiments.ipynb
```

---

## 10. Config Parameters Used

```
vision.cop_vision_radius
vision.thief_vision_radius
q_table.enabled
experiments.thief_style     # "honest" | "vague" | "deceptive"
experiments.placement       # "random" | "close" | "max_distance"
gui.enabled
gui.screenshot_dir
```

---

## 11. Test Plan

| Test | Type | Description |
|------|------|-------------|
| `test_config_overlay_applied` | unit | Case B sets cop_vision_radius=0 correctly |
| `test_metrics_all_fields_present` | unit | metrics.json has all required keys |
| `test_screenshot_saved_on_trigger` | unit | on_cop_wins saves PNG to correct path |
| `test_runner_runs_all_cases` | integration | All 7 cases complete with metrics saved |
| `test_summary_csv_has_7_rows` | integration | summary.csv has one row per experiment |

---

## 12. File Layout

```
src/cop_thief/experiments/
├── __init__.py
├── runner.py          # CLI entry point; iterates over cases
├── cases.py           # EXPERIMENT_CASES dict + config overlay logic
├── metrics.py         # Metrics collection and serialization
└── graphs.py          # matplotlib graph generation

src/cop_thief/gui/
└── screenshot.py      # PIL.ImageGrab capture (shared with GUI PRD)

notebooks/
└── experiments.ipynb

results/               # auto-created on first run
assets/screenshots/    # auto-created on first run
```

Each file stays under 150 code lines.
