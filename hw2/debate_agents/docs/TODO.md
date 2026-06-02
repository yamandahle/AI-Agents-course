# TODO — AI Debate System (HW2)

Status legend: [ ] = pending  [x] = done  [~] = in progress
Priority: P0 = blocker  P1 = high  P2 = medium

---

## Phase 0 — Planning Docs (before any code)

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 01 | Write PRD.md | [x] | P0 | File exists, covers all 8 requirements |
| 02 | Write PLAN.md | [x] | P0 | Class diagram + IPC + JSON schema present |
| 03 | Write TODO.md | [x] | P0 | ≥ 30 tasks across all phases |
| 04 | Write PRD_father_agent.md | [x] | P0 | Inputs/outputs/edge cases covered |
| 05 | Write PRD_debate_agents.md | [x] | P0 | Pro and Con roles documented |
| 06 | Write PRD_gatekeeper.md | [x] | P0 | Rate limit strategy documented |
| 07 | Write PRD_logger_watchdog.md | [x] | P0 | Rotation + restart logic documented |
| 08 | Git commit planning docs | [x] | P0 | On branch yamandahle-hw2 |

---

## Phase 1 — Stage 1: Manual Debate

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 09–15 | Manual debate + transcript | [x] | P0 | See `../../stage1/` |

---

## Phase 2 — Stage 2: Claude CLI

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 16–23 | Claude CLI commands + docs | [x] | P0 | See `../../.claude/commands/` |

---

## Phase 3 — Stage 3: Full Python Automation

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 24 | Initialize UV project | [x] | P0 | `uv sync` succeeds |
| 25 | Create .env-example and .gitignore | [x] | P0 | `.env-example` committed |
| 26 | Create config/ files | [x] | P0 | Three JSON files version 1.00 |
| 27 | Implement ConfigManager | [x] | P0 | Version validation on load |
| 28 | Write tests for ConfigManager | [~] | P0 | Covered indirectly via integration |
| 29 | Implement DebateMessage | [x] | P0 | `models.py` |
| 30–31 | ApiGatekeeper + tests | [x] | P0 | Rate limit, cost log |
| 32–33 | DebateLogger + tests | [x] | P0 | Rotation tested |
| 34–37 | BaseAgent, Pro, Con + tests | [x] | P0 | Unit + integration |
| 38–39 | FatherAgent + tests | [x] | P0 | Routing, verdict, detection |
| 40 | Watchdog | [x] | P1 | `watchdog.py` + unit tests |
| 41 | SDK entry point | [x] | P0 | CLI uses `DebateSDK` via `DebateRunner` adapter |
| 42 | CLI menu | [x] | P0 | `src/main.py` |
| 43 | Integration test (10 rounds) | [x] | P0 | Mocked 3-round + full pipeline tests |

---

## Phase 4 — Quality and Submission

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 44 | Run ruff — zero errors | [x] | P0 | `uv run ruff check .` |
| 45 | pytest ≥ 85% coverage | [x] | P0 | 161 tests, ~86% |
| 46 | Cost table in README | [x] | P0 | From actual run log |
| 47 | Final ruff + pytest | [x] | P0 | See `results/test_results.txt` |
| 48 | .gitignore covers secrets | [x] | P0 | `.env`, keys, credentials |
| 49 | Git commit final submission | [ ] | P0 | User pushes to GitHub |
| 50 | Add menu screenshots to assets/ | [ ] | P1 | PNG files in `assets/` |

---

Additional PRD files: see also `../../docs/PRD_*.md` and `PLAN.md` at the `hw2/` level.
