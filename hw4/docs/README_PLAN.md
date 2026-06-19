---
title: README Plan
version: "1.00"
status: in-progress
---

# README plan

I write `README.md` at the end. I save artifacts below as I work and tick boxes here.

**Target repo:** `cookiecutter/cookiecutter` only.

Legend: ✅ saved · ⬜ not yet

---

## README sections (final order)

1. Summary — EX04, graph-guided agents, cookiecutter
2. Install — `uv sync`, `.env` from `.env-example`
3. Usage — Grphify, agents, verify, Obsidian vault
4. Config — `config/setup.json`, `config/rate_limits.json`, `.env`
5. Why cookiecutter — architecture hubs, graph quality, one focused fix
6. Bug and root cause — HUB on `cookiecutter()` in `main.py`
7. Architecture — block diagram, OOP schema, communities from graph
8. Grphify + Obsidian — `index.md`, `hot.md`, edge types
9. Agent workflow — graph first, code second, token comparison
10. Fix — patch + short explanation
11. Verification — hub metrics after code fix
12. Tests — pytest ≥85%, ruff zero errors
13. Extensions — one original idea
14. License and credits

---

## Submission rules (guidelines V3)

- [x] SDK entry point, ApiGatekeeper for external calls
- [x] Config in JSON, secrets in `.env`, no hardcoded values
- [x] Files ≤ 150 lines, version 1.00, `uv` only
- [x] `docs/PRD.md`, `docs/TODO.md`, mechanism PRDs
- [ ] `docs/PLAN.md` (umbrella — only `PLAN_*.md` exist so far)
- [ ] `docs/PROMPT_LOG.md` filled with real entries
- [x] Screenshots in `assets/` (partial — see below)

---

## Stage 0 — Docs

| Save | Path | Status |
|------|------|--------|
| PRD | `docs/PRD.md` | ✅ |
| Plans | `docs/PLAN_*.md` | ✅ |
| Tasks | `docs/TODO.md` | ✅ |
| Mechanism PRDs | `docs/PRD_grphify.md`, `PRD_crew_agents.md`, `PRD_bug_fix.md` | ✅ |
| Umbrella plan | `docs/PLAN.md` | ⬜ |
| Prompt log | `docs/PROMPT_LOG.md` | ⬜ template only |

---

## Stage 1 — Setup

| Save | Path | Status |
|------|------|--------|
| Lock file | `uv.lock` | ✅ |
| Config | `config/setup.json`, `config/rate_limits.json` | ✅ |
| Env template | `.env-example` | ✅ |

---

## Stage 2 — Grphify

Package-only scan: `data/cookiecutter/cookiecutter/` (18 files). This is the working graph.

| Save | Path | Status |
|------|------|--------|
| Graph | `artifacts/graph.json` | ✅ |
| Baseline copy | `artifacts/graph_before.json` | ✅ |
| Report + HTML | `artifacts/GRAPH_REPORT.md`, `artifacts/graph.html` | ✅ |
| Navigation | `artifacts/index.md`, `artifacts/hot.md` | ✅ |
| Obsidian | `obsidian/index.md`, `obsidian/hot.md` | ✅ |
| Metrics (pre-fix) | `results/metrics_before.json` | ✅ |
| Screenshot | `assets/obsidian_graph.png` | ✅ |
| Screenshot | `assets/graph_html.png` | ✅ |

---

## Stage 3 — Agents

| Save | Path | Status |
|------|------|--------|
| Agent output | `results/agent_run.json` | ✅ |
| Bugs found | `results/bugs.json` | ✅ |
| Fix proposals | `results/fix_proposals.json` | ✅ |
| Token comparison | `results/token_stats.json` | ✅ (combined naive + graph-guided) |
| Prompts | `docs/PROMPT_LOG.md` | ⬜ |

---

## Stage 4 — Fix

| Save | Path | Status |
|------|------|--------|
| Chosen proposal | `results/fix_proposal.json` | ✅ |
| Patch | `results/fix_diff.patch` | ✅ |
| Architecture report | `reports/architecture_analysis.md` | ⬜ |
| Diagrams | `assets/block_diagram.png`, `assets/oop_schema.png` | ⬜ |

**Bug chosen:** HUB on `cookiecutter()` in `main.py` — extract to `orchestration.py`.

---

## Stage 5 — Verify (after code fix)

| Save | Path | Status |
|------|------|--------|
| Graph after fix | `artifacts/graph_after.json` | ✅ |
| Metrics after | `results/metrics_after.json` | ✅ |
| Comparison | `results/metrics_comparison.json` | ✅ |
| Report | `reports/verification.md` | ✅ |
| Screenshot | `assets/tests_pass.png` | ⬜ |

---

## Stage 6 — README

| Save | Path | Status |
|------|------|--------|
| Final README | `README.md` | ⬜ |

```bash
uv run ruff check src/
uv run pytest tests/ --cov=src --cov-report=term-missing
```
