---
title: PRD — EX04 Reverse Engineering with Grphify + CrewAI
version: "1.00"
status: draft
---

# EX04 — Project Requirements Document

## 1. Goal

Analyze the architecture of a real Python project (`thefuck`, via `soarsmu/BugsInPy`) using the
Grphify tool, then deploy a CrewAI multi-agent crew to automatically detect architectural bugs
(SPOFs, overloaded hubs), propose and apply fixes, and verify the result.

## 2. Target Repository

- **Base repo (lecturer-approved):** `cookiecutter/cookiecutter`
- **Target project:** `cookiecutter`
- **Why cookiecutter:** 18 Python files, clear hub in `main.py`, clean readable graph, visible before/after improvement

## 3. Deliverables

| # | Deliverable | File/Location |
|---|-------------|---------------|
| 1 | Grphify outputs | `artifacts/graph.json`, `artifacts/index.md`, `artifacts/hot.md` |
| 2 | Obsidian vault | `obsidian/` |
| 3 | Architecture analysis report | `reports/architecture_analysis.md` |
| 4 | CrewAI agent results | `results/agent_run.json` |
| 5 | Fixed source + diff | `results/fix_diff.patch` |
| 6 | Verification report | `reports/verification.md` |
| 7 | Unit tests (≥85% coverage) | `tests/` |
| 8 | README | `README.md` |

## 4. Success Criteria

- Grphify produces a valid `graph.json` with at least 50 nodes and 3 edge types
- Obsidian vault opens and shows the interactive graph
- At least 1 architectural bug detected (SPOF or overloaded hub)
- Fix is proposed, applied, and documented
- Unit tests pass after the fix
- Coverage ≥ 85%
- Zero Ruff linter errors
- All files ≤ 150 lines

## 5. Constraints

- `uv` is the ONLY package manager
- All API calls through `ApiGatekeeper`
- No hardcoded values (config from JSON, secrets from `.env`)
- OOP design, DRY, max 150 lines per file
- Version starts at `1.00`
- Each phase ends with a git commit

## 6. Out of Scope

- GUI or web interface
- Modifying BugsInPy repo (read-only clone)
- Fixing Python bugs (only architectural / structural bugs)
