---
title: PRD — Fix metrics_improved always returning false
version: "1.00"
status: approved
---

# Problem

The Quality Gate agent always produces `metrics_improved: false` and
`metrics_delta: {}`, causing every pipeline run to emit `verdict: FAIL` even
when tests pass and coverage is above 85%.

## Root causes

### RC-1 — Missing context for "before" metrics
`verification_task` has `context=[bug_detection_task, fix_proposal_task]`.
The graph summary produced by `graph_navigator` (node_count, edge_count,
community_count) is **not in the agent's context**. The agent cannot compare
before vs. after because it has no "before" values.

### RC-2 — graph_after.json does not exist during Stage 2
The pipeline stages are:
1. Stage 1: graphify scan → `graph.json`
2. Stage 2: CrewAI crew (4 agents) — Quality Gate is the **last agent here**
3. Stage 3: FixApplierService — applies the fix to the codebase
4. Stage 4: VerifyService — runs graphify again → `graph_after.json`

The Quality Gate currently instructs the agent to call
`Load Graph Metrics on graph_after_path`. But `graph_after.json` is created in
Stage 4, **after** the crew finishes. At the time the agent runs, that file
does not exist.

## Solution

Replace the impossible "compare before/after graph files" check with a
check the agent **can** perform at Stage 2 time:

- **Before metrics**: already in context via `graph_summary_task`
- **Improvement signal**: the fix proposal's `estimated_degree_reduction > 0`
  is a reliable proxy for whether the structural fix will improve graph metrics

### PASS criteria (updated)

| Criterion | Source |
|---|---|
| `tests_passed == true` | Run Unit Tests tool |
| `coverage_percent >= 85` | Run Unit Tests tool |
| `fix_is_valid == true` | fix proposal has `target_file` + `estimated_degree_reduction > 0` |

### metrics_delta output (updated)

Instead of comparing two graph JSON files, output the "before" hub degree from
the graph summary and the expected reduction from the fix proposal:

```json
{
  "top_hub_degree_before": 21,
  "estimated_degree_reduction": 5,
  "top_hub_degree_after_estimate": 16
}
```

## Files changed

| File | Change |
|---|---|
| `src/hw4/crewai_tasks/tasks.py` | Add `graph_summary_task` to context; rewrite verification description |
| `tests/unit/test_crewai_tasks.py` | Update context chain assertion |
