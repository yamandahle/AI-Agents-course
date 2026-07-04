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
| 3 — Orchestrator + LLM | [TODO_phase3_orchestrator.md](TODO_phase3_orchestrator.md) | [ ] Not started |
| 4 — Q-Table Advisor | [TODO_phase4_qtable.md](TODO_phase4_qtable.md) | [~] Trainer + Advisor done; Integration/Performance blocked on Phase 3 |
| 5 — GUI | [TODO_phase5_gui.md](TODO_phase5_gui.md) | [ ] Not started |
| 6 — Gmail Report | [TODO_phase6_gmail.md](TODO_phase6_gmail.md) | [ ] Not started |
| 7 — Experiments | [TODO_phase7_experiments.md](TODO_phase7_experiments.md) | [ ] Not started |

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
- [ ] docs/PROMPTS.md (fill as we go — graded)

---

## Final Submission Checklist

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] Full game runs end-to-end headlessly with Ollama
- [ ] GUI shows live board with screenshots saved
- [ ] Gmail report received by lecturer after game
- [ ] All 7 experiment cases complete with graphs + notebook
- [ ] No hardcoded parameters (all in config/config.json)
- [ ] No secrets committed (.env git-ignored)
- [ ] version.py starts at 1.00
- [ ] Every function/class/module has a docstring
- [ ] Each .py file ≤ 150 code lines
- [ ] docs/PROMPTS.md filled with all significant prompts/decisions
- [ ] README.md written in repo root
