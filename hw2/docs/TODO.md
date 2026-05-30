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
| 08 | Git commit planning docs | [ ] | P0 | Commit hash exists on yamandahle-hw2 |

---

## Phase 1 — Stage 1: Manual Debate (Two Terminals)

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 09 | Write Father system prompt (manual) | [ ] | P0 | Prompt enforces routing, no-tie, intervention |
| 10 | Write Pro system prompt (manual) | [ ] | P0 | Prompt locks position, requires citation |
| 11 | Write Con system prompt (manual) | [ ] | P0 | Prompt locks position, requires citation |
| 12 | Run manual debate session (≥ 5 rounds) | [ ] | P0 | Full exchange logged in docs/stage1_session.md |
| 13 | Screenshot terminal sessions | [ ] | P1 | Screenshots saved in docs/screenshots/ |
| 14 | Document lessons learned from Stage 1 | [ ] | P1 | Notes on agent alignment risk observed |
| 15 | Git commit Stage 1 | [ ] | P0 | Commit: "feat: Stage 1 manual debate complete" |

---

## Phase 2 — Stage 2: Claude CLI Command (Semi-Automatic)

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 16 | Write Father Claude CLI slash command | [ ] | P0 | Command routes Pro/Con without manual input |
| 17 | Write Pro Claude CLI slash command | [ ] | P0 | Command accepts Father message, returns argument |
| 18 | Write Con Claude CLI slash command | [ ] | P0 | Command accepts Father message, returns argument |
| 19 | Test 3-round semi-auto flow | [ ] | P0 | Father → Pro → Father → Con verified in terminal |
| 20 | Document CLI session with screenshots | [ ] | P1 | Saved in docs/screenshots/ |
| 21 | Git commit Stage 2 | [ ] | P0 | Commit: "feat: Stage 2 CLI command debate" |

---

## Phase 3 — Stage 3: Full Python Automation

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 22 | Initialize UV project, write pyproject.toml | [ ] | P0 | `uv sync` succeeds, ruff config present |
| 23 | Create .env-example and .gitignore | [ ] | P0 | No secrets in repo; .env-example has placeholders |
| 24 | Create config/ files (3 JSON files) | [ ] | P0 | All params read from config, zero hardcoded values |
| 25 | Implement ConfigManager | [ ] | P0 | All config reads go through one class |
| 26 | Write tests for ConfigManager | [ ] | P0 | Happy path + missing key + bad file covered |
| 27 | Implement DebateMessage dataclass | [ ] | P0 | Schema matches PLAN.md; validates on construction |
| 28 | Implement ApiGatekeeper | [ ] | P0 | Rate limit, FIFO queue, token log all working |
| 29 | Write tests for ApiGatekeeper (≥ 85% cov) | [ ] | P0 | Rate limit hit, retry, token log all tested |
| 30 | Implement DebateLogger | [ ] | P0 | FIFO rotation, 20 files max, 500 lines per config |
| 31 | Write tests for DebateLogger | [ ] | P1 | Rotation trigger tested with mock filesystem |
| 32 | Implement BaseAgent ABC | [ ] | P0 | Abstract methods enforced; shared init works |
| 33 | Implement ProAgent with stats skill | [ ] | P0 | Skill visible in system prompt; web search wired |
| 34 | Implement ConAgent with psychology skill | [ ] | P0 | Skill visible in system prompt; web search wired |
| 35 | Write unit tests for Pro/ConAgent | [ ] | P0 | respond(), get_skill(), build_system_prompt() tested |
| 36 | Implement FatherAgent (orchestrate+intervene) | [ ] | P0 | Detects alignment; declares non-tie winner |
| 37 | Write unit tests for FatherAgent | [ ] | P0 | intervene(), judge(), route() all tested with mocks |
| 38 | Implement Watchdog | [ ] | P1 | Restart tested with simulated process death |
| 39 | Implement SDK entry point (sdk.py) | [ ] | P0 | `from debate.sdk import run_debate` works end-to-end |
| 40 | Implement CLI menu (main.py) | [ ] | P0 | Terminal menu lets user start debate or view logs |
| 41 | Run integration test (full 10-round debate) | [ ] | P0 | Debate completes; winner declared; no tie |

---

## Phase 4 — Quality and Submission

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 42 | Run ruff — fix all errors | [ ] | P0 | `ruff check .` returns zero errors |
| 43 | Run pytest — verify ≥ 85% coverage | [ ] | P0 | Coverage report shows ≥ 85% |
| 44 | Run full debate; capture cost data | [ ] | P0 | Token counts logged; cost table ready for README |
| 45 | Write README.md (factual, no overclaiming) | [ ] | P0 | Screenshots, cost table, session log included |
| 46 | Final ruff + pytest check | [ ] | P0 | Both pass cleanly |
| 47 | Verify .gitignore covers .env and artifacts | [ ] | P0 | `git status` shows no secrets staged |
| 48 | Git commit final submission | [ ] | P0 | Commit: "chore: final submission ready" |
