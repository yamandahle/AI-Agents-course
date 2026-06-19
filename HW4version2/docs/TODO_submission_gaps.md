---
title: TODO — Submission Gap Remediation
version: "1.00"
status: in-progress
---

# TODO — Submission Gap Remediation

## Phase 1 — Config (no test risk)

- [ ] GAP-5: Create `config/logging_config.json`
- [ ] GAP-6: Add version validation to `ConfigManager.__init__`
- [ ] GAP-6: Add version mismatch test to `tests/unit/test_config.py`

## Phase 2 — Source splits (affects coverage)

- [ ] GAP-1: Create `src/hw4/shared/git_ops.py` with extracted git helpers
- [ ] GAP-1: Update `generic_fix_applier.py` to import from `git_ops`
- [ ] GAP-1: Verify `generic_fix_applier.py` ≤ 150 lines and tests pass

## Phase 3 — Test file splits

- [ ] GAP-2: Split `test_generic_fix_applier.py` → keep ≤ 150 lines
- [ ] GAP-2: Create `test_generic_fix_applier_apply.py` with apply tests
- [ ] GAP-2: Split `test_crew_runner_v2.py` → keep ≤ 150 lines
- [ ] GAP-2: Create `test_crew_runner_v2_run.py` with run() tests
- [ ] GAP-2: Run `pytest` — all tests pass, coverage ≥ 85 %

## Phase 4 — Results and notebooks

- [ ] GAP-4: Enrich `results/token_stats.json` with cost breakdown
- [ ] GAP-3: Create `notebooks/analysis.ipynb`

## Phase 5 — Documentation

- [ ] GAP-7: Add `## Contributing` and `## License` sections to `README.md`

## Phase 6 — Final validation

- [ ] Run `uv run ruff check src/ tests/` → 0 errors
- [ ] Run `uv run pytest --cov=src --cov-report=term-missing` → ≥ 85 % coverage
- [ ] Verify all source files ≤ 150 lines
- [ ] Commit all changes to `nagham-hw4`

## Definition of Done

All items above checked. `ruff check` = 0 errors. `pytest` = all pass, coverage ≥ 85 %.
No source or test file > 150 lines. `notebooks/analysis.ipynb` renders without error.
