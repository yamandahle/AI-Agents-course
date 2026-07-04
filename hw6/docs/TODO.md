# TODO — Cop & Thief: Dual AI Agents via MCP (EX06)

**Version:** 1.0  
**Date:** 2026-07-03  
**Update this file** as tasks complete. Mark `[x]` when done.

---

## Phase Status Overview

| Phase | File | Status |
|-------|------|--------|
| 1 — Game Engine | [TODO_phase1_game_engine.md](TODO_phase1_game_engine.md) | [x] Done |
| 2 — MCP Servers | [TODO_phase2_mcp.md](TODO_phase2_mcp.md) | [x] Done |
| 3 — Orchestrator + LLM | [TODO_phase3_orchestrator.md](TODO_phase3_orchestrator.md) | [x] Done |
| 4 — Q-Table Advisor | [TODO_phase4_qtable.md](TODO_phase4_qtable.md) | [x] Done (trainer + advisor; not used in final runs) |
| 5 — GUI | [TODO_phase5_gui.md](TODO_phase5_gui.md) | [x] Done |
| 6 — Gmail Report | [TODO_phase6_gmail.md](TODO_phase6_gmail.md) | [x] Done |
| 7 — Experiments | [TODO_phase7_experiments.md](TODO_phase7_experiments.md) | [x] Done (3-case vision comparison) |

---

## Documentation Checklist

- [x] CLAUDE.md
- [x] docs/PRD.md
- [x] docs/PLAN.md
- [x] docs/TODO.md (this file)
- [x] docs/PRD_game_engine.md
- [x] docs/PRD_mcp_communication.md
- [x] docs/PRD_llm_orchestrator.md
- [x] docs/PRD_gui.md
- [x] docs/PRD_gmail_report.md
- [x] docs/PRD_experiments.md
- [x] docs/PROMPTS.md

---

## Final Submission Checklist

- [x] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [x] `uv run ruff check .` → 0 violations
- [x] Full game runs end-to-end with Ollama (5×5, 6 sub-games)
- [x] GUI shows live board (`--gui` used for official run)
- [x] Gmail report sent to lecturer ([gmail_log.json](../results/gmail_log.json))
- [x] All 3 experiment cases complete with graphs (see Phase 7)
- [x] No hardcoded parameters (all in config/config.json)
- [x] No secrets committed (.env git-ignored)
- [x] version.py starts at 1.00
- [x] Every function/class/module has a docstring
- [x] Each .py file ≤ 150 code lines
- [x] docs/PROMPTS.md filled with significant prompts/decisions
- [x] README.md written in repo root
