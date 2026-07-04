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

## 2026-07-04 — Phase 6 (Gmail Report): Steps 1-4

**Action:** Student completed the manual Google Cloud Console setup
(project created, Gmail API + Calendar API enabled per lecturer's videos,
OAuth consent screen configured External with `gmail.modify` +
`calendar` scopes, test user added, Desktop OAuth Client created,
`credentials.json` downloaded into `hw6/` — confirmed gitignored).

**Gap found:** `config.json`'s `reporting` section had `group_name` but no
`students` field, even though the PRD's JSON report schema requires a
`students` array. Added `"students": []` as a placeholder — needs real
names filled in before final submission.

**Action:** Implemented Steps 2-4:
1. `gmail/report_builder.py` — `ReportBuilder.build(game_result, config)`
   converts a `GameResult` into the PRD's JSON schema, excluding crashed
   sub-games and extracting `cop_messages`/`thief_messages` arrays from
   each sub-game's turn log.
2. `gmail/auth.py` — `GmailAuth.get_credentials()`, following the exact
   load/refresh/first-run-browser-flow pattern from the lecturer's own
   reference script in `google-api-guide.pdf` (page 15), adapted to a
   config-driven class instead of hardcoded file paths.
3. `gmail/sender.py` — `GmailSender.send(report, config)` builds the
   email (JSON-only body, no free text, per PRD) and sends it via the
   Gmail API.

**Decision:** generalized `ApiGatekeeper` (built in Phase 3 for LLM calls
only) with a new `call_sync(provider, func)` method, rather than building
a second, separate gatekeeper for Gmail.
**Reason:** CLAUDE.md requires *all* external API calls (LLM and Gmail)
go through one central gatekeeper. The original `call()` was hardcoded to
async `httpx` POSTs, but Gmail's `google-api-python-client` call is a
synchronous, completely different shape. `call_sync` wraps any blocking
callable (via `asyncio.to_thread`) under the same per-provider rate-limit/
retry/logging policy, keyed by a `provider` string — added a `gmail`
section to `config/rate_limits.json` alongside the existing `ollama` one.
This kept the existing LLM-facing `call()` method and its tests
untouched while making the "one gatekeeper for everything" rule literally
true instead of nominal.

**Result:** 161 tests passing, 0 ruff violations, 94.41% overall coverage.
`report_builder.py`, `auth.py`, `sender.py`, and the regenerated
`api_gatekeeper.py` are all at 100% coverage. All Google APIs are mocked
in tests — no real sends happened yet.

**Remaining for Phase 6:** Step 5 (first real OAuth browser flow, one-time
manual, will create the real `token.json`), Step 6 (end-to-end test — a
real game ending with a real email received), Step 7 sign-off.

---

## 2026-07-04 — Phase 6 Step 5, Wired Gmail into main.py, Live Validation

**Action:** Completed the real OAuth login (Step 5). First attempt hit
`Error 403: access_denied` — the signed-in Google account wasn't correctly
saved as a Test user on the OAuth consent screen; fixed on the student's
side, then the consent flow completed and `token.json` was created and
confirmed gitignored.

**Action:** Wired `ReportBuilder`/`GmailAuth`/`GmailSender` into
`main.py`'s `run_game()` — previously it only logged the result and never
actually sent anything. A failed send is logged but doesn't crash the
program, so a working game run is never hidden behind an email failure.

**Live validation:** Ran a quick throwaway-config smoke test (3x2 grid, 1
move, 1 sub-game) specifically to prove the real Gmail send path works
end-to-end with the real token — succeeded (`results/gmail_log.json`:
status "ok", timestamp logged), and the actual email reached the
lecturer's real inbox (confirmed by the student pasting its exact body
back). Note: this sent one small throwaway test report to
`rmisegal+uoh26b@gmail.com` — acceptable but worth being aware a stray
test email exists in the lecturer's inbox ahead of the real submission.

**Bug found — confirmed by two live runs, not a mock:** every
`cop_messages`/`thief_messages` array in every report was empty, across
both the tiny smoke test and (more convincingly) the student's full real
6-sub-game/25-move run — 88 turns, zero recorded messages. Root cause in
`mcp/tools.py`: the architecture correctly splits each turn into two MCP
tool calls (`send_message` then `make_move`/`place_barrier`, per the
assignment spec), but `make_move_impl`/`place_barrier_impl` never
received or forwarded the message into `SubGame.apply_cop_action(action,
message)`/`apply_thief_action(...)` — those default `message=""` when the
caller omits it, which the move/barrier tools always did. The message
*did* reach the opponent correctly (via `message_store`, used for the
next observation) — only the turn-log recording used for the Gmail
report was broken.

**Fix:** added a `pending_message` field to `GameContext`.
`send_message_impl` stashes the message there; `make_move_impl`/
`place_barrier_impl` read-and-clear it via a new `_take_pending_message()`
helper and pass it into `apply_*_action`. Keeps the two-call tool
architecture intact; backward compatible (new field defaults to `""`).
Added 4 regression tests exercising the real (non-mocked)
`send_message_impl`/`make_move_impl`/`place_barrier_impl` functions to
catch this class of bug going forward. Did not re-trigger a live run to
re-verify, to avoid sending yet another test email — the regression tests
exercise the exact code path the bug was in.

**Result:** 165 tests passing, 0 ruff violations, 93.40% overall coverage,
`tools.py` back to 100%.

---

## 2026-07-04 — Phase 4: Q-Table Advisor (built via nagham-hw6 in parallel with Phase 3)

**Action:** Implemented `sdk/q_table/trainer.py` (self-play Bellman/epsilon-greedy
training) and `sdk/q_table/advisor.py` (loads the trained table, returns a
natural-language hint), plus a shared `sdk/q_table/encoding.py` for state/action
encoding. TDD per `docs/TODO_phase4_qtable.md`'s prescribed test list, all green.
Trained for real: 10,000 self-play episodes, ~2s, saved to `config/q_table.npy`.

**Bug found + fixed:** an unmasked epsilon-greedy policy let the Cop wall itself into a
corner with its own barriers (3 barriers is enough to seal one off) — the base game
engine has no stalemate rule for a fully-boxed-in agent, so this crashed the trainer
with `InvalidMoveError` on a full 10,000-episode run (not caught by the small-grid unit
tests). Fixed by masking action selection to the Cop's currently-legal moves only, and
ending the episode cleanly (no Q-update) if that set is ever empty. Added 2 regression
tests for this.

**Performance proxy check** (real check needs Phase 3's orchestrator, which doesn't
exist yet): 200 self-play games with a uniform-random Cop vs. 200 with a
greedy-over-trained-Q-table Cop, both vs. a random Thief — cop win rate 62.0% →
98.5%. Confirms the table is actually learning something useful, ahead of wiring it
into the real LLM prompt in Phase 3's `PromptBuilder`.

**Reason:** Student and teammate agreed to split remaining work in parallel — this side
takes Phase 4, teammate takes Phase 3 — accepting the risk that Phase 4 formally depends
on Phase 3's interfaces (per this file's own dependency graph) for the sake of pace.
`QTableAdvisor.get_hint(cop_pos, thief_pos)` is ready to be called from Phase 3's prompt
builder once it exists.

---

## 2026-07-04 — Phase 5: GUI (built via nagham-hw6, same parallel-with-Phase-3 split)

**Action:** Implemented `gui/game_state.py` (new `GameState` dataclass),
`gui/screenshot.py` (`ScreenshotCapture`, injectable `grab_fn`), `gui/board_view.py`
(tkinter Canvas grid renderer, cell-color logic separated from actual widget drawing),
`gui/info_panel.py` (score/message/turn/move-counter, same pure-logic/widget split),
and `gui/app.py` (`GuiApp`, wires the three together, headless-safe). TDD per
`docs/TODO_phase5_gui.md`'s prescribed test list, all green, plus an extra
`test_gui_app.py` for the headless path (not in the original list).

**Deviation:** PRD_gui.md assumes `game_session.on_state_change(callback)`, which
doesn't exist on `GameSession` yet (Phase 1 predates the GUI; Phase 3's game loop isn't
built). Added `GuiApp.update(state: GameState)` as the integration seam instead of
inventing a callback mechanism inside the already-signed-off game engine. Also dropped
`GameState.board: list[list[CellState]]` from the PRD spec — the real `GameBoard`
implementation never grew a `CellState`/`get_cell()` interface, so `BoardView` derives
cell colors directly from `cop_position`/`thief_position`/`barriers` instead.

**Environment note:** `PIL.ImageGrab.grab()` cannot actually capture the screen in this
sandbox (`OSError: X get_image failed`), even though real `tkinter` `Tk()`
windows/canvases genuinely can be created and rendered to here. Verified the full
render path live (`GuiApp(config, ...).update(state)` with a real window, correct
canvas sizing, no crash) — just couldn't produce real screenshot files or *see* the
window. `ScreenshotCapture` takes an injectable `grab_fn` so its own logic is fully
unit-tested regardless of what the real `ImageGrab.grab()` can do in a given
environment.

**Reason:** Same team split as Phase 4 — this side takes Phase 5 in parallel with
teammate's Phase 3, per PLAN.md's Member 2 assignment (Q-table, GUI, experiments).

---

## 2026-07-04 — Merged Phase 4+5, Wired Q-Table + GUI Into the Orchestrator

**Action:** Merged `feature/q-table-advisor-phase4` (Nagham's Phase 4 + Phase 5)
into `yamandahle-hw6`. One trivial conflict in `docs/PROMPTS.md` (both sides
appended entries independently); resolved by keeping both. 195 tests passing
post-merge, 0 ruff violations, 89.71% coverage.

**Gap found:** neither `QTableAdvisor` nor `GuiApp` was actually connected to
`GameLoop`/`main.py` — both were built and fully tested in isolation on
their own branch, but nothing in the running game ever called them.

**Action:** Wired both in:
1. `GameLoop` takes an optional `advisor: QTableAdvisor`. Before each Cop
   turn, `fallback.get_q_hint()` computes the hint from the **true** board
   positions (`sub_game.board.get_agent_pos`), not the Cop's own fog-of-war
   observation — matching the PRD's `get_hint(cop_pos, thief_pos)` signature
   exactly. This is a deliberate exception to fog-of-war: the advisor is a
   strategic-assist layer, not part of the agent's in-character senses.
2. `GameLoop.run()` takes an optional `on_turn` callback, invoked after every
   successful turn with a `GameState` snapshot (built by a new
   `orchestrator/live_state.py`) — `main.py` wires this straight to
   `GuiApp.update`.
3. `main.py`'s `--gui`/`--headless` flags now actually toggle
   `config["gui"]["enabled"]` (previously no-ops that only logged a warning).

**Refactor:** `game_loop.py` grew past the 150-code-line cap with this
wiring. Split out `orchestrator/fallback.py` (Q-hint computation, the
random-valid-action fallback, and random start-position picking — all
decision-support helpers, not core loop logic) and
`orchestrator/live_state.py` (GameState snapshot builder). `game_loop.py`
itself is back to 149 lines, each new module under 35.

**Live validation — the whole project confirmed working together in one
run for the first time:** trained a real Q-table (`uv run python -m
cop_thief.sdk.q_table.trainer`, 10k episodes, ~instant), enabled
`q_table.enabled` and ran `--headless` — completed cleanly with the real
trained table loaded and consulted every Cop turn (no crash, correct
scores). Then ran again with `--gui` — a real tkinter window was created,
updated every turn, and closed cleanly; no threading/Tcl errors. Both
runs also re-confirmed the message-log fix (turns now show real message
text) and real Gmail sending. Used a temporary test recipient +
throwaway grid/move counts for these checks; config restored to
production values (5x5, 6 games, 25 moves, real recipient,
`q_table.enabled: false`) afterward.

**Result:** 197 tests passing, 0 ruff violations, 89.59% overall coverage.

---

<!-- Add new entries below as development progresses -->

---

## 2026-07-04 — Fast 3-experiment submission path

**Decision:** Minimal submission set — 1 full 5×5 (6 sub-games) + 2 small-grid
vision comparisons (3×2, 2 sub-games each), instead of all 7 Phase-7 cases.

**Speed choices:**
- Model `qwen2.5:0.5b` in experiment configs (pulled via Ollama).
- `gmail.enabled: false` on small runs; only Exp 1 emails the lecturer.
- `--config experiments/<name>.json` flag on `main.py`; results auto-saved to
  `results/<name>/result.json`.
- Ollama rate limit raised to 120 calls/min for batch runs.

**Smoke test:** Exp 2 completed in ~56 s (Cop 25, Thief 15).

---

## 2026-07-05 — Phase 7 reduced: 3 cases + graphs (no 7-case marathon)

**Decision:** Experiments PRD/TODO updated to **3 vision-comparison cases**
(exp1 5×5 baseline, exp2 blind cop 3×2, exp3 full vision 3×2) instead of
7 full 5×5 cases A–G. Keeps comparison + 4 graphs (`win_rates`,
`score_comparison`, `vision_vs_winrate`, `capture_turn_dist`).

**Implementation:** `src/cop_thief/experiments/{cases,metrics,graphs,runner}.py`
+ tests. `--graphs-only` builds summary/charts from existing `result.json`.

**Run order for student:** Exp 2 & 3 with `--gui`, then `--graphs-only`.
