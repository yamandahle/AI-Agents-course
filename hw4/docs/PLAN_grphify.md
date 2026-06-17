---
title: PLAN — Grphify Stage
version: "1.00"
status: draft
---

# Grphify Stage Plan

## Goal
Clone the target Python project, run Grphify on it, and set up the Obsidian
vault for visual architecture analysis.

## Prerequisites
- Scaffold stage complete
- `uv` initialized

## Steps

### 1. Add Grphify dependency
Add `grphify` to the project using uv.

### 2. Clone the source repository
Clone `soarsmu/BugsInPy` into `data/BugsInPy/`.
Use BugsInPy's setup script to extract the `thefuck` project source
into `data/thefuck/`.

### 3. Run Grphify
Run Grphify on `data/thefuck/` and direct outputs to `artifacts/`.
Expected outputs: `graph.json`, `index.md`, `hot.md`.

### 4. Validate outputs
Confirm `graph.json` has at least 50 nodes and all 3 edge types present
(`Extracted`, `Inferred`, `Ambiguous`).

### 5. Set up Obsidian vault
Copy Grphify markdown outputs into `obsidian/`.
Open the folder as an Obsidian vault and confirm the graph view renders.

### 6. Implement `GraphBuilderService`
File: `src/hw4/services/graph_builder.py`

Methods:
- Clone the repo
- Run Grphify CLI
- Parse `graph.json` into a `Graph` dataclass
- Compute graph metrics (degree, centrality, communities, bridges)

All subprocess calls go through `ApiGatekeeper`.

### 7. Implement graph data models
File: `src/hw4/models/graph_models.py`

Define dataclasses: `Node`, `Edge`, `Graph`, `GraphMetrics`.

### 8. Write unit tests
File: `tests/unit/test_graph_builder.py`

Test graph loading and metric computation using a small mock `graph.json`.

## Done Checklist
- [ ] `artifacts/graph.json` exists with ≥ 50 nodes
- [ ] Obsidian vault opens and graph renders
- [ ] `GraphBuilderService` implemented and tested
- [ ] Unit tests pass
- [ ] Zero Ruff errors

## Git Commit
```
feat: add Grphify stage — clone thefuck, generate graph artifacts
```

## Next
`PLAN_agents.md` — build the CrewAI agent crew
