# TODO — Phase 7: Experiments (3-case vision comparison)

**PRD:** [PRD_experiments.md](PRD_experiments.md)  
**Status:** [x] Done

---

## 1. Config + cases

- [x] `config/experiments/exp1_full_5x5.json`
- [x] `config/experiments/exp2_small_blind_cop.json`
- [x] `config/experiments/exp3_small_full_vision.json`
- [x] `src/cop_thief/experiments/cases.py`
- [x] `tests/unit/test_experiment_cases.py`

---

## 2. Metrics

- [x] `src/cop_thief/experiments/metrics.py`
- [x] `tests/unit/test_metrics.py`

---

## 3. Graphs (4 charts)

- [x] `src/cop_thief/experiments/graphs.py`
- [x] `tests/unit/test_graphs.py`
- [x] Charts: `win_rates`, `score_comparison`, `vision_vs_winrate`, `capture_turn_dist`

---

## 4. Runner

- [x] `src/cop_thief/experiments/runner.py`
- [x] `tests/integration/test_experiment_runner.py`
- [x] CLI: `--case`, `--all`, `--graphs-only`, `--gui`

---

## 5. Run experiments

- [x] Exp 1 — full 5×5 + Gmail (`results/exp1_full_5x5/result.json`)
- [x] Exp 2 — blind cop, small grid (`results/exp2_small_blind_cop/result.json`)
- [x] Exp 3 — full vision, small grid (`results/exp3_small_full_vision/result.json`)
- [x] `uv run python -m cop_thief.experiments.runner --graphs-only`
- [x] Verify `results/summary.csv` has **3 rows**
- [x] Verify 4 PNGs in `results/graphs/`

---

## 6. README + analysis

- [x] README documents all 3 experiments + conclusion
- [x] Graphs embedded in README
- [x] Links to result.json / metrics.json per case

---

## 7. Phase 7 sign-off

- [x] `uv run pytest tests/ --cov` → ≥ 85%
- [x] `uv run ruff check .` → 0 violations
- [x] All 3 cases have `result.json` + graphs
- [x] Update [TODO.md](TODO.md) Phase 7 status
