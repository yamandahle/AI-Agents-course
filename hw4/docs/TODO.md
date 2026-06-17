---
title: TODO — EX04 Task List
version: "1.00"
status: in-progress
---

# TODO — EX04 Reverse Engineering with Grphify + CrewAI

## Stage 0 — Docs & Planning
- [x] Write `docs/PRD.md`
- [x] Write `docs/PRD_grphify.md`
- [x] Write `docs/PRD_crew_agents.md`
- [x] Write `docs/PRD_bug_fix.md`
- [x] Write `docs/PLAN_scaffold.md`
- [x] Write `docs/PLAN_grphify.md`
- [x] Write `docs/PLAN_agents.md`
- [x] Write `docs/PLAN_bug_fix.md`
- [x] Write `docs/PLAN_verify.md`
- [x] Write `docs/TODO.md`

## Stage 1 — Setup (see PLAN_scaffold.md)
- [ ] Run `uv init .` inside `hw4/`
- [ ] Create full folder structure (`src/hw4/`, `tests/`, `config/`, etc.)
- [ ] Write `shared/version.py` — `VERSION = "1.00"`
- [ ] Write `config/setup.json` — version, agent config, paths
- [ ] Write `config/rate_limits.json` — openai + github rate limits
- [ ] Configure `pyproject.toml` — dependencies, Ruff, coverage
- [ ] Write `.env-example`
- [ ] Write `.gitignore`
- [ ] Write skeleton stubs — `sdk.py`, `gatekeeper.py`, all agent files
- [ ] Verify `uv run python -c "import hw4"` works
- [ ] Verify `uv run ruff check src/` → zero errors
- [ ] Git commit: `feat: init hw4 project setup v1.00`

## Stage 2 — Grphify (see PLAN_grphify.md)
- [ ] Add `grphify` dependency via uv
- [ ] Clone `soarsmu/BugsInPy` into `data/BugsInPy/`
- [ ] Extract `thefuck` source into `data/thefuck/`
- [ ] Run Grphify → produce `artifacts/graph.json`, `index.md`, `hot.md`
- [ ] Validate graph has ≥ 50 nodes and all 3 edge types
- [ ] Set up Obsidian vault in `obsidian/`
- [ ] Implement `src/hw4/services/graph_builder.py`
- [ ] Implement `src/hw4/models/graph_models.py`
- [ ] Write `tests/unit/test_graph_builder.py`
- [ ] Git commit: `feat: add Grphify stage — clone thefuck, generate graph artifacts`

## Stage 3 — Agents (see PLAN_agents.md + PRD_crew_agents.md)
- [ ] Implement `src/hw4/agents/graph_reader.py` — Agent 1
- [ ] Implement `src/hw4/agents/bug_detector_agent.py` — Agent 2
- [ ] Implement `src/hw4/agents/fix_proposer.py` — Agent 3
- [ ] Implement `src/hw4/agents/verifier.py` — Agent 4
- [ ] Implement `src/hw4/services/crew_runner.py` — assemble the crew
- [ ] Wire all LLM calls through `ApiGatekeeper`
- [ ] Write unit tests for each agent (mock inputs, no real LLM)
- [ ] Git commit: `feat: add CrewAI agents — graph reader, bug detector, fix proposer, verifier`

## Stage 4 — Bug Fix (see PLAN_bug_fix.md + PRD_bug_fix.md)
- [ ] Implement `src/hw4/services/bug_detector.py` — SPOF, hub, bridge detection
- [ ] Implement `src/hw4/services/fix_applier.py` — apply fix, save diff
- [ ] Add `detect_bugs()` and `apply_fix()` to `sdk/sdk.py`
- [ ] Save `results/bugs.json`, `results/fix_proposal.json`, `results/fix_diff.patch`
- [ ] Write `tests/unit/test_bug_detector.py`
- [ ] Write `tests/unit/test_fix_applier.py`
- [ ] Git commit: `feat: add bug detection and fix applier services`

## Stage 5 — Verify (see PLAN_verify.md)
- [ ] Save baseline metrics to `results/metrics_before.json`
- [ ] Re-run Grphify on fixed source → `artifacts/graph_after.json`
- [ ] Compare metrics → `results/metrics_comparison.json`
- [ ] Run full test suite — all pass, coverage ≥ 85%
- [ ] Run Ruff — zero errors
- [ ] Write `reports/verification.md`
- [ ] Update `README.md` with findings and metrics summary
- [ ] Git commit: `feat: add verification stage — re-run Grphify, compare metrics, final report`
