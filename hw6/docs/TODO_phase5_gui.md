# TODO — Phase 5: GUI

**Dependency:** Phase 3 complete.  
**PRD:** [PRD_gui.md](PRD_gui.md)  
**Status:** [~] Screenshot/BoardView/InfoPanel/App done; manual validation partially blocked
**Can run in parallel with:** Phase 4 (Q-Table)

**Notes on deviations (see `nagham-hw6` branch, `HW6/docs/PROMPTS.md` for full context):**
- PRD_gui.md assumes `game_session.on_state_change(callback)`, which doesn't exist on
  `GameSession` (Phase 1 predates the GUI, and Phase 3's game loop isn't built yet).
  Added `GuiApp.update(state: GameState)` as the integration seam instead — any caller
  (demo script, test, or eventually the real orchestrator) pushes a `GameState` there.
  New `src/cop_thief/gui/game_state.py` defines that dataclass (all PRD fields except
  `board: list[list[CellState]]`, which was dropped — the actual `GameBoard`
  implementation never grew a `CellState`/`get_cell()` interface; `BoardView` derives
  cell colors directly from `cop_position`/`thief_position`/`barriers` instead).
- Built and verified in an environment where `PIL.ImageGrab.grab()` cannot actually grab
  the screen (sandboxed X11, `OSError: X get_image failed`) even though real `tkinter`
  windows/canvases CAN be created and rendered to. `ScreenshotCapture` takes an
  injectable `grab_fn` so it's fully unit-testable regardless; the actual
  `on_subgame_start`/etc. calls work correctly when run somewhere `ImageGrab.grab()`
  really works (confirmed the render path end-to-end with a real `Tk()` + `Canvas`,
  just not the final pixel grab).

---

## 1. Screenshot Module (TDD) -- DONE

- [x] `pillow` already present in pyproject.toml
- [x] `assets/screenshots/` already exists (has content from the Phase 2 HTTP demo)
- [x] Write `tests/unit/test_screenshot.py` FIRST (red):
  - `test_screenshot_saves_png_to_correct_path`
  - `test_screenshot_filename_includes_case_and_sg_number`
  - `test_screenshot_dir_created_if_missing`
  - `test_all_5_triggers_produce_files`
- [x] Implement `src/cop_thief/gui/screenshot.py` (green):
  - `ScreenshotCapture` class
  - Methods: `on_subgame_start`, `on_barrier_placed`, `on_cop_wins`, `on_thief_wins`, `on_game_end`
  - Uses `PIL.ImageGrab.grab()` (injectable) → saves to `assets/screenshots/<case>/<filename>.png`
- [x] Refactor — 39 code lines
- [x] `uv run ruff check` → 0 violations

---

## 2. Board View (TDD) -- DONE

- [x] Write `tests/unit/test_board_view.py` FIRST (red):
  - `test_cop_cell_colored_blue`
  - `test_thief_cell_colored_red`
  - `test_barrier_cell_colored_gray`
  - `test_empty_cell_colored_white`
  - `test_board_dimensions_match_config`
- [x] Implement `src/cop_thief/gui/board_view.py` (green):
  - tkinter Canvas-based grid renderer
  - `cell_color()` is pure logic (testable with `canvas=None`); `render()` touches
    the real Canvas, only exercised at runtime
  - Reads `GameState` and draws cells
  - Uses `config.gui.cell_size_px` for dimensions
- [x] Refactor — 47 code lines
- [x] `uv run ruff check` → 0 violations

---

## 3. Info Panel (TDD) -- DONE

- [x] Write `tests/unit/test_info_panel.py` FIRST (red):
  - `test_score_panel_shows_correct_scores`
  - `test_message_panel_shows_both_agents`
  - `test_turn_indicator_shows_correct_agent`
  - `test_move_counter_updates`
- [x] Implement `src/cop_thief/gui/info_panel.py` (green):
  - Score labels, message text boxes, turn indicator, move counter
  - Text-formatting methods are pure logic; `render()` touches real widgets
  - Updates from `GameState` via `GuiApp.update()` (see deviation note above)
- [x] Refactor — 50 code lines
- [x] `uv run ruff check` → 0 violations

---

## 4. Main App -- DONE

- [x] Implement `src/cop_thief/gui/app.py` (green):
  - Wires `BoardView` + `InfoPanel` + `ScreenshotCapture`
  - `update(state)` seam instead of subscribing to `on_state_change` (doesn't exist yet)
  - `run_in_background()` starts tkinter main loop in a separate daemon thread
  - `close()` exits cleanly
- [x] Headless mode: `gui.enabled = false` → no tkinter object created at all
- [x] Refactor — 58 code lines
- [x] `uv run ruff check` → 0 violations
- [x] Added `tests/unit/test_gui_app.py` (not in this file's original list) covering
  the headless path fully — the only part testable without a real display

---

## 5. Manual Validation -- partially done, partially blocked

- [x] Live-verified (not just unit tests): real `Tk()` root + `Canvas` created,
  `GuiApp.update(state)` called with cop/thief/barrier positions, no crash, canvas
  sized correctly (200x200 for a 5x5 grid at 40px cells) — done headlessly by calling
  the render path directly, since there's no way to *see* a window in this environment
- [x] **GUI validated on real display:** official 5×5 run with `--gui`
- [ ] Auto-screenshots via `PIL.ImageGrab` — optional; manual screenshots not saved

---

## 6. Phase 5 Sign-off

- [x] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [x] `uv run ruff check .` → 0 violations
- [x] GUI runs with `--gui` on real display (official 5×5 run)
- [x] Headless mode unchanged
- [x] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 5 — tkinter GUI + screenshot capture"`
- [ ] Push to `yamandahle-hw6`
- [x] Update [TODO.md](TODO.md) phase status to `[x] Done`
