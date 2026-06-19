---
title: PLAN — Bug Fix Stage
version: "1.00"
status: draft
---

# Bug Fix Stage Plan

## Goal
Detect architectural bugs using pure Python graph algorithms, apply the
proposed fix to the source, and save the result.

## Prerequisites
- Agents stage complete
- `results/fix_proposal.json` exists from Agent 3

## Steps

### 1. Implement `BugDetectorService`
File: `src/hw4/services/bug_detector.py`

Pure Python using `networkx` — no LLM calls.
Detects three bug types:
- **SPOF:** node whose removal disconnects the graph
- **Hub:** node with degree above the configured threshold
- **Weak Bridge:** single edge connecting two otherwise-disconnected communities

All thresholds come from `config/setup.json`.

### 2. Implement `FixApplierService`
File: `src/hw4/services/fix_applier.py`

Applies the fix proposal from Agent 3 to the actual source files:
- Creates a git branch named after the bug type and node
- Applies the refactoring change (move or split file)
- Saves a diff to `results/fix_diff.patch`
- Commits the change

All git subprocess calls go through `ApiGatekeeper`.

### 3. Update `sdk/sdk.py`
Add `detect_bugs()` and `apply_fix()` methods to the SDK.

### 4. Save results
- `results/bugs.json` — full list of detected bugs
- `results/fix_proposal.json` — the chosen fix
- `results/fix_diff.patch` — git diff of the applied change

### 5. Write unit tests
- `tests/unit/test_bug_detector.py` — test each detection method with a
  small hardcoded graph that has a known SPOF, hub, and bridge
- `tests/unit/test_fix_applier.py` — test that the patch file is created
  and the fix result is returned correctly

## Done Checklist
- [ ] At least 1 bug detected in the cookiecutter graph
- [ ] Fix applied and `results/fix_diff.patch` saved
- [ ] `results/bugs.json` and `results/fix_proposal.json` saved
- [ ] All unit tests pass
- [ ] Zero Ruff errors
- [ ] All files ≤ 150 lines

## Git Commit
```
feat: add bug detection and fix applier services
```

## Next
`PLAN_verify.md` — re-run Grphify and verify the fix worked
