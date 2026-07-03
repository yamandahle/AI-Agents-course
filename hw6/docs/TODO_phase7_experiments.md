# TODO — Phase 7: Experiments

**Dependency:** Phases 4, 5, 6 complete.  
**PRD:** [PRD_experiments.md](PRD_experiments.md)  
**Status:** [ ] Not started

---

## 1. Config Overlay System (TDD)

- [ ] Write `tests/unit/test_experiment_cases.py` FIRST (red):
  - `test_case_A_uses_vision_radius_2`
  - `test_case_B_sets_cop_vision_to_0`
  - `test_case_C_sets_full_vision`
  - `test_case_D_enables_q_table`
  - `test_case_E_sets_deceptive_style`
  - `test_config_overlay_does_not_mutate_base`
  - `test_all_7_cases_defined`
- [ ] Implement `src/cop_thief/experiments/cases.py` (green):
  - `EXPERIMENT_CASES` dict (7 entries A–G)
  - `apply_overlay(base_config, case_overrides) -> dict`
  - Returns new config dict without modifying original
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 2. Metrics Collection (TDD)

- [ ] Write `tests/unit/test_metrics.py` FIRST (red):
  - `test_metrics_has_all_required_fields`
  - `test_cop_wins_count_correct`
  - `test_avg_capture_turn_calculated`
  - `test_metrics_saved_to_json`
  - `test_summary_csv_row_has_case_name`
- [ ] Implement `src/cop_thief/experiments/metrics.py` (green):
  - `MetricsCollector.collect(game_result, case_name) -> dict`
  - `MetricsCollector.save(metrics, results_dir)`
  - `MetricsCollector.append_to_summary_csv(metrics, results_dir)`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 3. Graph Generator (TDD)

- [ ] Write `tests/unit/test_graphs.py` FIRST (red):
  - `test_win_rate_chart_saved`
  - `test_score_comparison_chart_saved`
  - `test_vision_vs_winrate_chart_saved`
  - `test_rl_impact_chart_saved`
  - `test_charts_saved_to_correct_dir`
- [ ] Implement `src/cop_thief/experiments/graphs.py` (green):
  - `GraphGenerator.generate_all(summary_csv_path, output_dir)`
  - Produces: `win_rates.png`, `score_comparison.png`,
    `capture_turn_dist.png`, `vision_vs_winrate.png`, `rl_impact.png`
  - Uses `matplotlib` + `seaborn`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 4. Experiment Runner (TDD)

- [ ] Write `tests/integration/test_experiment_runner.py` FIRST (red):
  - `test_runner_runs_single_case`
  - `test_runner_runs_all_cases`
  - `test_metrics_file_created_per_case`
  - `test_summary_csv_has_7_rows`
- [ ] Implement `src/cop_thief/experiments/runner.py` (green):
  - CLI: `--all` or `--case <name>`
  - For each case: apply overlay → run GameSession → collect metrics → save
  - After all cases: generate all graphs
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 5. Run All Experiment Cases

- [ ] Ensure Ollama is running: `ollama serve`
- [ ] Run Case A (baseline): `uv run python -m cop_thief.experiments.runner --case A_baseline`
  → `results/A_baseline/metrics.json` created
- [ ] Run Case B: `--case B_blind_cop`
- [ ] Run Case C: `--case C_full_vision`
- [ ] Run Case D: `--case D_rl_cop`
- [ ] Run Case E: `--case E_deceptive`
- [ ] Run Case F: `--case F_close_start`
- [ ] Run Case G: `--case G_max_distance`
- [ ] Run all at once: `uv run python -m cop_thief.experiments.runner --all`
- [ ] Verify `results/summary.csv` has 7 rows
- [ ] Verify all 5 graphs exist in `results/graphs/`

---

## 6. Screenshots Verification

- [ ] After running all cases, verify `assets/screenshots/` contains:
  - One folder per case (7 folders)
  - Each folder has: `sg1_start.png` through `sg6_start.png`
  - Capture/escape screenshots where applicable
  - `final_score.png` for each case
- [ ] Select best screenshots for notebook and README

---

## 7. Experiments Notebook

- [ ] Create `notebooks/experiments.ipynb`
- [ ] Cell 1: Load `results/summary.csv`, display as table
- [ ] Cell 2: Reproduce `win_rates.png` inline
- [ ] Cell 3: Reproduce `score_comparison.png` inline
- [ ] Cell 4: Reproduce `vision_vs_winrate.png` inline
- [ ] Cell 5: Reproduce `rl_impact.png` inline
- [ ] Cell 6: Written analysis — did each hypothesis hold? (A–G)
- [ ] Cell 7: Conclusion — which config favors Cop? Which favors Thief? Why?
- [ ] Cell 8: Display key screenshots inline (`IPython.display.Image`)
- [ ] Run all cells top-to-bottom → no errors
- [ ] `uv run jupyter nbconvert --to notebook --execute notebooks/experiments.ipynb`
  → executes cleanly

---

## 8. Phase 7 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] All 7 cases have results + screenshots
- [ ] All 5 graphs generated
- [ ] Notebook runs end-to-end with written analysis
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 7 — experiments, graphs, notebook"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) all phases to `[x] Done`
