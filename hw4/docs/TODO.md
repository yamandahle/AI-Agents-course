---
title: TODO — EX04 Task List
version: "1.00"
status: in-progress
---

# TODO — EX04 Reverse Engineering with Grphify + CrewAI

Legend: `[x]` = done · `[ ]` = still to do

---

## Stage 0 — Docs & Planning ✅
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
- [x] Write `docs/README_PLAN.md`
- [ ] Write `docs/PLAN.md` (umbrella plan — mentioned in submission guidelines V3)
- [ ] Fill `docs/PROMPT_LOG.md` with real prompt entries

## Stage 1 — Setup ✅
- [x] Run `uv init .` inside `hw4/`
- [x] Create full folder structure (`src/hw4/`, `tests/`, `config/`, etc.)
- [x] Write `shared/version.py` — `VERSION = "1.00"`
- [x] Write `config/setup.json` — version, agent config, paths
- [x] Write `config/rate_limits.json` — openai + github rate limits
- [x] Configure `pyproject.toml` — dependencies, Ruff, coverage
- [x] Write `.env-example`
- [x] Write `.gitignore`
- [x] Write skeleton stubs — `sdk.py`, `gatekeeper.py`, all agent files
- [x] Verify `uv run python -c "import hw4"` works
- [x] Verify `uv run ruff check src/` → zero errors
- [x] Git commit: `feat: init hw4 project setup v1.00`

## Stage 2 — Grphify ✅
- [x] Add `grphify` dependency via uv (`graphifyy`)
- [x] Clone `cookiecutter` source into `data/cookiecutter/`
- [x] Run Grphify package-only → `data/cookiecutter/cookiecutter/` (18 files)
- [x] Save graph → `artifacts/graph.json`
- [x] Save report + HTML → `artifacts/GRAPH_REPORT.md`, `artifacts/graph.html`
- [x] Save baseline copy → `artifacts/graph_before.json`
- [x] Save full-repo backup → `artifacts/graph_full_repo_backup.json`
- [x] Copy navigation → `artifacts/index.md`, `artifacts/hot.md`
- [x] Set up Obsidian vault → `obsidian/index.md`, `obsidian/hot.md`, `obsidian/GRAPH_REPORT.md`
- [x] Save pre-fix metrics → `results/metrics_before.json`
- [x] Screenshots → `assets/obsidian_graph.png`, `assets/graph_html.png`
- [x] Implement `src/hw4/services/graph_builder.py`
- [x] Implement `src/hw4/models/graph_models.py`
- [x] Write `tests/unit/test_graph_builder.py` — 6 tests pass
- [x] Git commit: `feat: add Grphify stage — graph artifacts, GraphBuilderService, unit tests`
- [x] Git commit: `feat(hw4): package-only graph, CrewAI agents, and agent results` (pushed)

## Stage 3 — Agents ✅
- [x] Implement `src/hw4/agents/graph_reader.py` — Agent 1
- [x] Implement `src/hw4/agents/bug_detector_agent.py` — Agent 2
- [x] Implement `src/hw4/agents/fix_proposer.py` — Agent 3
- [x] Implement `src/hw4/agents/verifier.py` — Agent 4
- [x] Implement `src/hw4/services/crew_runner.py` — assemble the crew
- [x] Implement `src/hw4/models/agent_models.py`
- [x] Implement `src/hw4/shared/llm_client.py` — LLM via ApiGatekeeper
- [x] Wire all LLM calls through `ApiGatekeeper`
- [x] Wire `HW4SDK.run_agents()` and `detect_bugs()`
- [x] Save `results/agent_run.json`
- [x] Save `results/bugs.json`
- [x] Save `results/fix_proposals.json`
- [x] Save `results/token_stats.json` (naive vs graph-guided comparison)
- [x] Write unit tests — graph_reader, bug_detector, bug_detector_agent, fix_proposer, crew_runner, verifier, sdk, config, llm_client
- [x] All agent files ≤ 150 lines
- [x] Pushed to GitHub (included in commit `1b277d6`)

## Stage 4 — Bug Fix ✅
- [x] Implement `src/hw4/services/bug_detector.py` — SPOF, hub, bridge detection
- [x] Implement `src/hw4/services/fix_applier.py` — apply fix, save diff
- [x] Implement `src/hw4/services/cookiecutter_refactor.py` + templates in `resources/*.txt`
- [x] Add `apply_fix()` to `sdk/sdk.py`
- [x] Choose bug: HUB on `cookiecutter()` in `main.py`
- [x] Apply refactor → `orchestration.py` + thin `main.py`
- [x] Git branch in cookiecutter clone → `fix/hub-cookiecutter`
- [x] Save `results/fix_proposal.json`
- [x] Save `results/fix_diff.patch`
- [x] Write `tests/unit/test_fix_applier.py`
- [x] All files ≤ 150 lines
- [ ] Git commit hw4 Stage 4 changes (fix_applier, verify not yet pushed)

## Stage 5 — Verify ✅
- [x] Implement `src/hw4/services/verify_service.py`
- [x] Implement `src/hw4/services/verify_report.py`
- [x] Wire `HW4SDK.verify()`
- [x] Re-run Grphify on fixed package (`graphify update`)
- [x] Save `artifacts/graph_after.json`
- [x] Save `results/metrics_after.json`
- [x] Save `results/metrics_comparison.json`
- [x] Write `reports/verification.md`
- [x] Run unit tests — 24 pass, coverage ≥ 85%
- [x] Run Ruff — zero errors
- [x] Write `tests/unit/test_verify_service.py`
- [ ] Git commit hw4 Stage 5 changes

## Stage 6 — README & submission (remaining)

### Must have (PRD + guidelines V3)
- [ ] Write `README.md` from `docs/README_PLAN.md`
- [ ] Git push all Stage 4–5 code + results + reports

### Recommended (README_PLAN deliverables)
- [ ] Write `reports/architecture_analysis.md`
- [ ] Screenshot `assets/tests_pass.png` (pytest output)
- [ ] Diagrams `assets/block_diagram.png`, `assets/oop_schema.png` (optional but in plan)

### Nice to have
- [ ] Implement `HW4SDK.run_grphify()` (currently stub — verify uses graphify directly)
- [ ] Write `docs/PLAN.md` umbrella document
- [ ] Fill `docs/PROMPT_LOG.md`

---

## Quick gap check (all PLAN files)

| PLAN file | Key deliverable | Status |
|-----------|-----------------|--------|
| `PLAN_scaffold.md` | uv, config, skeleton | ✅ done |
| `PLAN_grphify.md` | graph.json, Obsidian, GraphBuilderService | ✅ done |
| `PLAN_agents.md` | 4 agents, crew_runner, JSON results | ✅ done |
| `PLAN_bug_fix.md` | bug_detector, fix_applier, patch | ✅ done |
| `PLAN_verify.md` | graph_after, metrics compare, verification.md | ✅ done |
| `README_PLAN.md` | README.md final write-up | ❌ not started |
| Submission guidelines | PROMPT_LOG, PLAN.md, architecture report | ⚠️ partial |

---

## Git commits still needed

| Commit message | What to include |
|----------------|-----------------|
| `feat: add bug detection and fix applier services` | fix_applier, cookiecutter_refactor, Stage 4 tests |
| `feat: add verification stage — re-run Grphify, compare metrics, final report` | verify_service, graph_after, metrics, verification.md |
| `docs: add README and final submission artifacts` | README.md, architecture_analysis.md, PROMPT_LOG |
