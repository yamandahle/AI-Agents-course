---
title: PLAN — Fix metrics_improved
version: "1.00"
---

# Implementation plan

## Step 1 — Fix tasks.py: add graph_summary_task to context

`verification_task` currently has:
```python
context=[bug_detection_task, fix_proposal_task]
```
Change to:
```python
context=[graph_summary_task, bug_detection_task, fix_proposal_task]
```

## Step 2 — Rewrite verification task description

Remove the instruction to call `Load Graph Metrics` on `graph_after_path`
(file doesn't exist yet). Replace with instructions that:

1. Run unit tests → get tests_passed + coverage_percent
2. Extract "before" hub degree from the graph summary already in context
3. Read estimated_degree_reduction from the fix proposal already in context
4. Compute metrics_delta from those two values
5. Set metrics_improved = (estimated_degree_reduction > 0)
6. Verdict: PASS if all three criteria met; FAIL with retry_instruction otherwise

## Step 3 — Update test_crewai_tasks.py

The context chain assertion currently checks:
```python
assert len(call_records[3]) == 2  # verification: context = [bug_detection, fix_proposal]
```
Update to:
```python
assert len(call_records[3]) == 3  # verification: context = [graph_summary, bug_detection, fix_proposal]
```
