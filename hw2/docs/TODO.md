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
| 08 | Git commit planning docs | [x] | P0 | Commit 0bc9e4e on yamandahle-hw2 |

---

## Phase 1 — Stage 1: Manual Debate (Two Terminals)

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 09 | Write Father system prompt (manual) | [x] | P0 | HOW_TO_RUN.md — human acts as Father |
| 10 | Write Pro system prompt (manual) | [x] | P0 | stage1/pro_prompt.md — pasted into ChatGPT |
| 11 | Write Con system prompt (manual) | [x] | P0 | stage1/con_prompt.md — pasted into Gemini |
| 12 | Run manual debate session (≥ 5 rounds) | [x] | P0 | stage1/debate_transcript.md — 5 rounds logged |
| 13 | Save session as transcript | [x] | P1 | stage1/debate_transcript.md complete |
| 14 | Document lessons learned from Stage 1 | [x] | P1 | stage1/observations.md — winner CON 8/10 |
| 15 | Git commit Stage 1 | [x] | P0 | Commit 8f3c210 on yamandahle-hw2 |

---

## Phase 2 — Stage 2: Claude CLI Command (Semi-Automatic)

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 16 | Write Father Claude CLI slash command | [x] | P0 | .claude/commands/father_skill.md |
| 17 | Write Pro Claude CLI slash command | [x] | P0 | .claude/commands/pro_skill.md |
| 18 | Write Con Claude CLI slash command | [x] | P0 | .claude/commands/con_skill.md |
| 19 | Write start_debate main command | [x] | P0 | .claude/commands/start_debate.md |
| 20 | Add JSON format, context window, timer, interventions | [x] | P0 | All added to father_skill + start_debate |
| 21 | Document CLI session with screenshots | [x] | P1 | assets/stage2/ — 6 screenshots saved |
| 22 | Write README.md for project | [x] | P0 | Complete guide for unfamiliar reader |
| 23 | Git commit Stage 2 | [x] | P0 | Commits b2d9fbd → 15e17e6 on yamandahle-hw2 |

---

## Phase 3 — Stage 3: Full Python Automation

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 24 | Initialize UV project, write pyproject.toml | [x] | P0 | `uv sync` succeeds, ruff config present |
| 25 | Create .env-example and .gitignore | [x] | P0 | No secrets in repo; .env-example has placeholders |
| 26 | Create config/ files (3 JSON files) | [x] | P0 | All params read from config, zero hardcoded values |
| 27 | Implement ConfigManager | [ ] | P0 | All config reads go through one class |
| 28 | Write tests for ConfigManager | [ ] | P0 | Happy path + missing key + bad file covered |
| 29 | Implement DebateMessage dataclass | [ ] | P0 | Schema matches PLAN.md; validates on construction |
| 30 | Implement ApiGatekeeper | [x] | P0 | Rate limit, FIFO queue, token log all working |
| 31 | Write tests for ApiGatekeeper (≥ 85% cov) | [x] | P0 | Rate limit hit, retry, token log all tested |
| 32 | Implement DebateLogger | [ ] | P0 | FIFO rotation, 20 files max, 500 lines per config |
| 33 | Write tests for DebateLogger | [ ] | P1 | Rotation trigger tested with mock filesystem |
| 34 | Implement BaseAgent ABC | [ ] | P0 | Abstract methods enforced; shared init works |
| 35 | Implement ProAgent with stats skill | [ ] | P0 | Skill visible in system prompt; web search wired |
| 36 | Implement ConAgent with psychology skill | [ ] | P0 | Skill visible in system prompt; web search wired |
| 37 | Write unit tests for Pro/ConAgent | [ ] | P0 | respond(), get_skill(), build_system_prompt() tested |
| 38 | Implement FatherAgent (orchestrate+intervene) | [ ] | P0 | Detects alignment; declares non-tie winner |
| 39 | Write unit tests for FatherAgent | [ ] | P0 | intervene(), judge(), route() all tested with mocks |
| 40 | Implement Watchdog | [ ] | P1 | Restart tested with simulated process death |
| 41 | Implement SDK entry point (sdk.py) | [ ] | P0 | `from debate.sdk import run_debate` works end-to-end |
| 42 | Implement CLI menu (main.py) | [ ] | P0 | Terminal menu lets user start debate or view logs |
| 43 | Run integration test (full 10-round debate) | [ ] | P0 | Debate completes; winner declared; no tie |

---

## Phase 4 — Quality and Submission

| # | Task | Status | Priority | Definition of Done |
|---|------|--------|----------|--------------------|
| 44 | Run ruff — fix all errors | [ ] | P0 | `ruff check .` returns zero errors |
| 45 | Run pytest — verify ≥ 85% coverage | [ ] | P0 | Coverage report shows ≥ 85% |
| 46 | Run full debate; capture cost data | [ ] | P0 | Token counts logged; cost table added to README |
| 47 | Final ruff + pytest check | [ ] | P0 | Both pass cleanly |
| 48 | Verify .gitignore covers .env and artifacts | [ ] | P0 | `git status` shows no secrets staged |
| 49 | Git commit final submission | [ ] | P0 | Commit: "chore: final submission ready" |
