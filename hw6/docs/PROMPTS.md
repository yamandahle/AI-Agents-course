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

<!-- Add new entries below as development progresses -->
