---
title: README Plan
version: "1.00"
status: in-progress
---

# README plan

I write `README.md` at the end. I save artifacts below as I work and tick boxes here.

**Target repo:** `cookiecutter/cookiecutter` only.

---

## README sections (final order)

1. Summary — EX04, graph-guided agents, cookiecutter
2. Install — `uv sync`, `.env` from `.env-example`
3. Usage — Grphify, agents, verify, Obsidian vault
4. Config — `config/setup.json`, `config/rate_limits.json`, `.env`
5. Why cookiecutter — architecture hubs, graph quality, one focused fix
6. Bug and root cause — SPOF or overloaded hub in `main.py` / `generate.py`
7. Architecture — block diagram, OOP schema, communities from graph
8. Grphify + Obsidian — `index.md`, `hot.md`, edge types
9. Agent workflow — graph first, code second, token comparison
10. Fix — patch + short explanation
11. Before / after — hub degree, SPOF count, screenshots
12. Tests — pytest ≥85%, ruff zero errors
13. Extensions — one original idea
14. License and credits

---

## Submission rules (guidelines V3)

- SDK entry point, ApiGatekeeper for external calls
- Config in JSON, secrets in `.env`, no hardcoded values
- Files ≤ 150 lines, version 1.00, `uv` only
- `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md`, mechanism PRDs
- `docs/PROMPT_LOG.md` for AI prompts
- Screenshots in `assets/`

---

## Stage 0 — Docs

| Save | Path |
|------|------|
| PRD | `docs/PRD.md` |
| Plans | `docs/PLAN_*.md` |
| Tasks | `docs/TODO.md` |
| Mechanism PRDs | `docs/PRD_grphify.md`, `PRD_crew_agents.md`, `PRD_bug_fix.md` |

---

## Stage 1 — Setup

| Save | Path |
|------|------|
| Lock file | `uv.lock` |
| Config | `config/setup.json`, `config/rate_limits.json` |
| Env template | `.env-example` |

---

## Stage 2 — Grphify

| Save | Path |
|------|------|
| Before graph | `artifacts/graph_before.json` |
| Report + HTML | `artifacts/GRAPH_REPORT.md`, `artifacts/graph.html` |
| Obsidian | `obsidian/index.md`, `obsidian/hot.md` |
| Baseline metrics | `results/metrics_before.json` |
| Screenshots | `assets/obsidian_graph.png`, `assets/hub_before.png` |

Scan path: `data/cookiecutter/cookiecutter/` (18 source files).

---

## Stage 3 — Agents

| Save | Path |
|------|------|
| Agent output | `results/agent_run.json` |
| Bugs found | `results/bugs.json` |
| Naive tokens | `results/token_naive.json` |
| Graph-guided tokens | `results/token_graph_guided.json` |
| Prompts | `docs/PROMPT_LOG.md` |

---

## Stage 4 — Fix

| Save | Path |
|------|------|
| Proposal | `results/fix_proposal.json` |
| Patch | `results/fix_diff.patch` |
| Architecture report | `reports/architecture_analysis.md` |
| Diagrams | `assets/block_diagram.png`, `assets/oop_schema.png` |

---

## Stage 5 — Verify

| Save | Path |
|------|------|
| After graph | `artifacts/graph_after.json` |
| Metrics | `results/metrics_after.json`, `results/metrics_comparison.json` |
| Report | `reports/verification.md` |
| Screenshot | `assets/hub_after.png`, `assets/tests_pass.png` |

---

## Stage 6 — README

I compile `README.md` from everything above.

```bash
uv run ruff check src/
uv run pytest tests/ --cov=src --cov-report=term-missing
```
