# PRD — Experiments (3-case vision comparison)

**Mechanism:** Experiment Runner & Analysis  
**Version:** 1.1  
**Date:** 2026-07-05  
**Status:** Active — reduced scope (3 cases, not 7)

---

## 1. Purpose

Compare how **vision radius** affects Cop vs Thief outcomes using three
config-driven runs — one official 5×5 baseline plus two fast small-grid
contrasts. Results, comparison graphs, and logs are saved under `results/`.

---

## 2. Experiment cases (3 total)

| Case | Config | Grid | Vision (cop / thief) | Sub-games | Hypothesis |
|------|--------|------|----------------------|-----------|------------|
| **exp1_full_5x5** | `config/experiments/exp1_full_5x5.json` | 5×5 | 2 / 2 | 6 × 25 | Baseline balanced play |
| **exp2_small_blind_cop** | `config/experiments/exp2_small_blind_cop.json` | 3×2 | **0 / 2** | 2 × 10 | Blind cop → thief advantage |
| **exp3_small_full_vision** | `config/experiments/exp3_small_full_vision.json` | 3×2 | **2 / 2** | 2 × 10 | Full vision → cop advantage vs Exp 2 |

Only **exp1** sends Gmail (`gmail.enabled: true`). Small runs disable email.

---

## 3. Metrics per case

| Metric | Description |
|--------|-------------|
| `cop_wins` / `thief_wins` | Sub-game win counts |
| `cop_win_rate` | cop_wins / num_sub_games |
| `cop_total_score` / `thief_total_score` | Cumulative scores |
| `avg_capture_turn` | Mean moves when cop wins |
| `avg_moves_per_subgame` | Mean moves per sub-game |
| `barriers_used_avg` | Mean barriers per sub-game |

Saved to `results/<case_name>/metrics.json`. Game log: `results/<case_name>/result.json`.

---

## 4. Aggregate outputs

- `results/summary.csv` — one row per case (3 rows)
- `results/graphs/`:
  - `win_rates.png` — cop vs thief wins per case
  - `score_comparison.png` — total scores per case
  - `vision_vs_winrate.png` — cop win rate vs cop vision radius
  - `capture_turn_dist.png` — histogram of capture turns

**Not in scope:** 7-case matrix, Q-table comparison graph, RL impact chart.

---

## 5. Screenshots

Manual (GUI runs): save to `results/<case_name>/screenshots/`.

---

## 6. How to run

```powershell
# Run one case
uv run python -m cop_thief.experiments.runner --case exp2_small_blind_cop --gui

# Run all 3 (exp1 takes longest)
uv run python -m cop_thief.experiments.runner --all --gui

# Build graphs from existing result.json files (no re-run)
uv run python -m cop_thief.experiments.runner --graphs-only
```

---

## 7. File layout

```
src/cop_thief/experiments/
├── cases.py      # 3 case names + config paths
├── metrics.py    # collect + summary.csv
├── graphs.py     # 4 comparison charts
└── runner.py     # CLI

config/experiments/
├── exp1_full_5x5.json
├── exp2_small_blind_cop.json
└── exp3_small_full_vision.json

results/
├── summary.csv
├── graphs/*.png
├── exp1_full_5x5/{result.json, metrics.json, screenshots/}
├── exp2_small_blind_cop/...
└── exp3_small_full_vision/...
```

Each code file ≤ 150 lines.
