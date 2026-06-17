---
title: PLAN — Verify Stage
version: "1.00"
status: draft
---

# Verify Stage Plan

## Goal
Re-run Grphify on the fixed source, compare before/after graph metrics,
run unit tests, and produce the final verification report.

## Prerequisites
- Bug fix stage complete
- `results/fix_diff.patch` exists
- Original `artifacts/graph.json` saved as baseline

## Steps

### 1. Save baseline metrics
Before re-running Grphify, save the original graph metrics to
`results/metrics_before.json` for comparison.

### 2. Re-run Grphify on the fixed source
Run Grphify again on `data/thefuck/` after the fix is applied.
Save new outputs to `artifacts/graph_after.json`.

### 3. Compare metrics
Compare before and after:
- Did the hub degree decrease?
- Did the SPOF count decrease?
- Did the bridge count stay the same or improve?
- Did the number of connected components stay the same?

Save comparison to `results/metrics_comparison.json`.

### 4. Run unit tests
Run the full test suite on the fixed source:
```
uv run pytest tests/ --cov=src --cov-report=term-missing
```
All tests must pass and coverage must be ≥ 85%.

### 5. Run Ruff
```
uv run ruff check src/
```
Zero errors required.

### 6. Write verification report
File: `reports/verification.md`

Include:
- Bug that was fixed (type, node, severity)
- Metrics before and after
- Test results (pass/fail, coverage %)
- Conclusion: did the fix improve the architecture?

### 7. Update README
Add a summary section to `README.md` with:
- What was found
- What was fixed
- Key metrics comparison

## Done Checklist
- [ ] `artifacts/graph_after.json` exists
- [ ] `results/metrics_comparison.json` shows improvement
- [ ] All unit tests pass
- [ ] Coverage ≥ 85%
- [ ] Zero Ruff errors
- [ ] `reports/verification.md` written
- [ ] `README.md` updated

## Git Commit
```
feat: add verification stage — re-run Grphify, compare metrics, final report
```

## Next
`TODO.md` — full task list across all stages
