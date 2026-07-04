# PROMPTS — Decision Log (EX06)

This file logs all significant prompts and decisions made during development.
It is a graded requirement — update it after every meaningful decision.

---

## 2026-07-03 — Documentation Phase

**Decision:** Use Approach 3 (hybrid/local) for LLM architecture.  
**Reason:** No external exposure needed during development; swap to cloud via config.

**Decision:** Q-table as optional tactical advisor (injected into LLM prompt).  
**Reason:** Assignment recommends it (Section 8); keeps LLM as final decision-maker.

**Decision:** tkinter for GUI framework.  
**Reason:** Zero extra dependency (stdlib); sufficient for 5×5 grid display.

**Decision:** Q-table state = (cop_row, cop_col, thief_row, thief_col) only — no barriers.  
**Reason:** Keeps state space at 625 entries; barriers change per sub-game making Q-table unstable if included.

**Decision:** 7 experiment cases (A–G) covering vision radius, Q-table on/off, thief deception, initial placement.  
**Reason:** Shows diverse outcome scenarios required by assignment originality section.

---

## 2026-07-04 — Phase 2 Verification: MCP Servers Over Real HTTP

**Action:** Manually verified both MCP servers work over real network transport
(not just in-process), using a 3-terminal test:
- Terminal 1: `uv run python scripts/start_cop_demo.py` (cop server, port 8001)
- Terminal 2: `uv run python scripts/start_thief_demo.py` (thief server, port 8002)
- Terminal 3: `uv run python scripts/call_servers.py` (MCP client calling both)

**Result:** All tool calls succeeded (`list_tools`, `get_observation`,
`send_message`, `make_move`, `place_barrier`) — see
`assets/screenshots/mcp_3terminal_test.png` and full call log in
`results/mcp_demo.json`.

**Reason:** Confirms the client/server MCP architecture (LLM will live in the
orchestrator client, not in the servers) actually works across process
boundaries before building Phase 3 on top of it.

---

## Working agreement — screenshots & prompt logging

**Decision:** Claude proactively flags when a screenshot is worth capturing
at each milestone/update, and logs important prompts/decisions into this
file as they happen, rather than waiting to be asked.
**Reason:** Student requested this on 2026-07-04 to keep the graded prompt
log and visual evidence trail complete without manual reminders each time.

---

## 2026-07-04 — Merged Nagham's Gap Fixes + Phase 3 Started (Steps 1–4)

**Action:** Fetched and merged Nagham's `fix/mcp-auth-and-gaps` branch (already
on `main` via PR #18: Bearer token auth wired into both MCP servers, a ruff
cleanup, and `TooManyCrashesError` handling) into `yamandahle-hw6`, fixed one
leftover ruff violation, then fast-forward merged the combined branch into
`main`. No conflicts; 86 tests green before and after.

**Decision:** Switched `config.json` `llm.model` from `llama3` to `phi3:mini`.  
**Reason:** Only `phi3:mini` was actually pulled in local Ollama; smaller/
faster for iterative development, swappable via config later.

**Action:** Began Phase 3 (orchestrator). Completed, in TDD order:
1. `shared/config.py` — first-ever config-file loader in the repo (Phase 1–2
   code took values as constructor args directly; nothing read `config.json`
   until now).
2. `api_gatekeeper.py` — single choke point for LLM calls: rate limiting
   (sleeps rather than rejecting), retries, call logging, `ApiCallError`
   after retries exhausted.
3. `orchestrator/prompt_builder.py` — system + user prompt construction per
   the PRD's format, fog-of-war-aware opponent description, optional
   Q-table hint line.
4. `orchestrator/mcp_client.py` — thin async wrapper calling the cop/thief
   MCP servers as a client, attaching `authorization: Bearer <token>`.

**Bug found & fixed:** Discovered while building the MCP client that
Nagham's auth fix requires `authorization` as a **tool-call argument**, not
an HTTP header. This broke the already-pushed Phase 2 demo scripts
(`demo_mcp.py`, `scripts/call_servers.py`), which predate her fix. Fixed
both to send the argument; also fixed a pre-existing, previously-unexercised
bug in `demo_mcp.py`'s `show()` helper (assumed all results were iterable,
which only holds for `list_tools()`) and a Windows console encoding crash
from a `→`/`✓` character. Verified both scripts run cleanly end-to-end
(in-process and over real HTTP) after the fixes.

**Result:** 123 tests passing, 0 ruff violations, 97.64% coverage.

---

## 2026-07-04 — Merged Nagham's Independent Demo-Script Fix + Phase 3 Step 5

**Action:** Nagham independently found and fixed the same demo-script auth
bug on her own branch (`fix/demo-script-missing-token`, commit `ebfff06`),
covering `scripts/call_servers.py` only (not `demo_mcp.py`, which Claude's
fix already covered). Merged her branch into `yamandahle-hw6`; resolved a
trivial duplicate-`AUTH`-constant conflict in `call_servers.py` and a
timestamp-only conflict in `results/mcp_demo.json`. Her fix branch is now
redundant and safe to close. Pushed to `yamandahle-hw6` (not merged to
`main` — user asked to hold off merging to `main` until all phases are
finished, not after every step).

**Decision:** GameLoop drives sub-games by calling MCP tools only for agent
actions (`get_observation`, `send_message`, `make_move`/`place_barrier`),
but calls the game engine SDK directly (`is_terminal()`, `get_result()`)
for internal bookkeeping between turns.
**Reason:** Matches the assignment PDF's explicit requirement (Section 5.2)
that all agent decisions/actions flow through MCP tools while the
orchestrator/client owns turn management — bookkeeping isn't an agent
action, so it doesn't need to cross the MCP boundary. Also avoids double-
applying moves: reusing Phase 1's `GameSession.run()` as-is would have
applied each action twice (once via the MCP tool's internal call, once via
`GameSession`'s own direct `apply_*_action` call on the same shared
`SubGame`), since both would touch the identical object.

**Action:** Implemented Step 5 — `orchestrator/game_loop.py`. Reuses
`GameResult`/`SubGameResult`/`TooManyCrashesError` from Phase 1's
`game_session.py` rather than inventing new result types, so the eventual
Gmail report (Phase 6) can reuse `GameResult.to_dict()` unchanged. Added an
`on_complete` callback hook (invoked once after all sub-games finish) as
the seam Phase 6 will plug the Gmail sender into.

**Result:** 11 tests (7 from the TODO spec + 4 added for crash-handling,
barrier actions, and real `_random_starts` coverage), `game_loop.py` at
100% coverage. Full suite: 134 tests passing, 0 ruff violations, 98.01%
overall coverage.

---

## 2026-07-04 — Phase 3 Step 6 (Entry Point) + Step 7 Live Validation

**Action:** Implemented `src/main.py` — parses `--gui`/`--headless`/`--case`
flags, loads config, starts both MCP servers as real background asyncio
tasks on their configured ports (via FastMCP's `run_async`), builds the
gatekeeper/clients/GameLoop, and runs one full game. `--gui` and `--case`
log a "not implemented yet" warning for now (Phases 5 and 7).

**Bugs found and fixed via live end-to-end runs against real local Ollama
(phi3:mini)** — neither was ever hit by the mocked unit/integration tests,
only by actually running against a real, messy LLM:
1. `MessageTooLongError` crashed the whole sub-game whenever phi3:mini's
   "message" text rambled past `max_message_chars`. Fixed by truncating
   the message before calling `send_message`.
2. A syntactically valid but illegal action (e.g. `ACTION: N` when already
   at the grid edge) crashed the whole sub-game, because the Step 5 retry
   loop only retried on *unparseable* responses, never on the server
   rejecting an otherwise-well-formed action. Fixed by catching
   `fastmcp.exceptions.ToolError` around the actual MCP dispatch and
   retrying it through the same budget as parse failures; the final
   fallback (after all retries exhausted) now only picks a direction
   verified valid against the real board (`board.is_valid_move`), so the
   fallback itself can never be rejected.

**Result after fixes:** ran three live smoke tests against real Ollama —
3x2 grid (before/after the fix) and 4x3 grid — saved as
`results/step7_smoke_3x2_before_fix.log`,
`results/step7_smoke_3x2_after_fix.log`, `results/step7_smoke_4x3.log`
(trimmed to our own log lines + final result; raw output included a lot of
routine HTTP/MCP protocol noise). The 4x3 run happened to exercise the
full retry-exhaustion fallback path for real (thief failed all 3 retries,
fell back to a verified-valid move, game continued normally) — strong live
evidence the fix works, not just in mocked tests.

**Decision:** the full-size validation (real config: 5x5 grid, 6 sub-games,
25 moves each) was handed to the student to run themselves in their own
terminal, since a genuine run could take 30-90+ minutes with real LLM
calls and Claude's tool has a 10-minute execution limit.
**Reason:** avoids an artificially truncated/killed run; the student's
terminal has no such limit.

**Full test suite:** 140 tests passing, 0 ruff violations, 93.44% overall
coverage (`main.py` itself is naturally lower since its wiring/server-
startup code is validated by actually running it, not by mocks).

---

<!-- Add new entries below as development progresses -->
