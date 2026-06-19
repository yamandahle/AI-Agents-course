---
title: PLAN — EX04 Umbrella
version: "1.00"
status: complete
---

# PLAN — EX04 Reverse Engineering (umbrella)

This file links all stage plans. Each stage has its own detailed `PLAN_*.md`.

| Stage | Plan file | What it covers | Status |
|-------|-----------|----------------|--------|
| 0 | — | Docs, PRD, TODO | done |
| 1 | `PLAN_scaffold.md` | uv, config, SDK skeleton | done |
| 2 | `PLAN_grphify.md` | Clone cookiecutter, Grphify, artifacts | done |
| 3 | `PLAN_agents.md` | 4 CrewAI agents, crew_runner | done |
| 4 | `PLAN_bug_fix.md` | bug_detector, fix_applier, patch | done |
| 5 | `PLAN_verify.md` | Re-scan, metrics compare, verification | done |
| 6 | `README_PLAN.md` | README, screenshots, submission | done |

## Execution order

```
Setup → Grphify → Agents → Fix → Verify → README
```

## Key deliverables

| Deliverable | Location |
|-------------|----------|
| Graph (before) | `artifacts/graph.json` |
| Graph (after) | `artifacts/graph_after.json` |
| Agent results | `results/agent_run.json`, `bugs.json` |
| BugsInPy cross-check | `results/functional_bugs.json` |
| Fix patch | `results/fix_diff.patch` |
| Verification | `reports/verification.md` |
| Architecture report | `reports/architecture_analysis.md` |
| README | `README.md` |
| Prompt log | `docs/PROMPT_LOG.md` |

## Target

**Repository:** [cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)  
**Scan path:** `data/cookiecutter/cookiecutter/` (package only)
