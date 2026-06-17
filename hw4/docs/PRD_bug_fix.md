---
title: PRD — Bug Detection & Fix Mechanism
version: "1.00"
status: draft
---

# PRD — Architectural Bug Detection & Fix

## 1. Purpose

This document covers the algorithm for detecting architectural bugs in the graph,
proposing fixes, and verifying the result.

## 2. Bug Types We Detect

### 2.1 SPOF (Single Point of Failure)
- **Definition:** A node whose removal disconnects the graph (or a major subgraph)
- **Graph test:** Remove node → check if connected components increase
- **Threshold:** Any node that increases component count by ≥ 1 when removed
- **Example in cookiecutter:** `main.py` — all other modules depend on it

### 2.2 Overloaded Hub
- **Definition:** A node with degree (in + out edges) above a configured threshold
- **Graph test:** `degree(node) > hub_degree_threshold` (default: 10)
- **Risk:** One change breaks everything that depends on it
- **Example in cookiecutter:** `generate.py` — many modules import template utilities from it

### 2.3 Weak Bridge
- **Definition:** A single edge that connects two otherwise-disconnected communities
- **Graph test:** Bridge detection via DFS (Tarjan's algorithm)
- **Risk:** If that one file/function disappears, two entire modules lose contact

## 3. Detection Algorithm (`BugDetectorService`)

```
Input:  graph_summary (nodes, edges, communities, centrality)
Output: List[ArchitecturalBug]

Steps:
1. For each node with degree > threshold → flag as HUB
2. For each node: simulate removal → if components increase → flag as SPOF
3. Run bridge detection on edge list → flag weak bridges
4. Sort bugs by severity (HIGH first)
5. Return top-N bugs (configurable, default: 5)
```

## 4. Fix Proposal Algorithm (`FixProposerAgent`)

For each detected bug, the LLM agent proposes:

| Bug Type | Fix Strategy |
|----------|-------------|
| SPOF | Split into multiple smaller modules; add a facade that delegates |
| HUB | Extract responsibilities into separate service classes |
| WEAK_BRIDGE | Introduce a shared interface or adapter layer between communities |

The proposal names:
- Which file to change
- What class or function to extract
- Where the new file should go in the project structure

## 5. Fix Application (`FixApplierService`)

1. Read the fix proposal
2. Create a git branch: `fix/<bug-type>-<node-name>`
3. Apply the change (refactoring — no behavior change)
4. Commit with message: `refactor: fix <bug-type> in <node> (EX04)`
5. Save diff to `results/fix_diff.patch`

## 6. Verification (`VerifierAgent`)

After applying the fix:
1. Re-run Grphify on the modified source
2. Compare new `graph.json` vs original:
   - Did the hub's degree drop?
   - Did the SPOF get eliminated?
3. Run unit tests: `uv run pytest tests/ --tb=short`
4. Record: test pass/fail, centrality delta, edge count delta
5. Save `reports/verification.md`

## 7. Metrics to Compare

| Metric | Before | After | Goal |
|--------|--------|-------|------|
| Hub degree | X | < X | Decrease |
| SPOF count | N | N-1 | Decrease |
| Bridge count | B | ≤ B | Same or less |
| Connected components | C | ≤ C | Same |
| Unit tests pass | - | Yes | Must pass |

## 8. Success Criteria

- At least 1 bug detected
- At least 1 fix applied successfully (no crash)
- After fix: hub degree or SPOF count decreases
- Unit tests pass after fix
- Verification report saved
