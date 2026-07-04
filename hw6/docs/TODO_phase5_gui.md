# TODO — Phase 5: GUI

**Dependency:** Phase 3 complete.  
**PRD:** [PRD_gui.md](PRD_gui.md)  
**Status:** [ ] Not started  
**Can run in parallel with:** Phase 4 (Q-Table)

---

## 1. Screenshot Module (TDD)

- [ ] Add `pillow` to pyproject.toml if not already present
- [ ] Create `assets/screenshots/.gitkeep`
- [ ] Write `tests/unit/test_screenshot.py` FIRST (red):
  - `test_screenshot_saves_png_to_correct_path`
  - `test_screenshot_filename_includes_case_and_sg_number`
  - `test_screenshot_dir_created_if_missing`
  - `test_all_5_triggers_produce_files`
- [ ] Implement `src/cop_thief/gui/screenshot.py` (green):
  - `ScreenshotCapture` class
  - Methods: `on_subgame_start`, `on_barrier_placed`, `on_cop_wins`, `on_thief_wins`, `on_game_end`
  - Uses `PIL.ImageGrab.grab()` → saves to `assets/screenshots/<case>/<filename>.png`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 2. Board View (TDD)

- [ ] Write `tests/unit/test_board_view.py` FIRST (red):
  - `test_cop_cell_colored_blue`
  - `test_thief_cell_colored_red`
  - `test_barrier_cell_colored_gray`
  - `test_empty_cell_colored_white`
  - `test_board_dimensions_match_config`
- [ ] Implement `src/cop_thief/gui/board_view.py` (green):
  - tkinter Canvas-based grid renderer
  - Reads `GameState` and draws cells
  - Uses `config.gui.cell_size_px` for dimensions
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 3. Info Panel (TDD)

- [ ] Write `tests/unit/test_info_panel.py` FIRST (red):
  - `test_score_panel_shows_correct_scores`
  - `test_message_panel_shows_both_agents`
  - `test_turn_indicator_shows_correct_agent`
  - `test_move_counter_updates`
- [ ] Implement `src/cop_thief/gui/info_panel.py` (green):
  - Score labels, message text boxes, turn indicator, move counter
  - Updates from `GameState` via callback
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 4. Main App

- [ ] Implement `src/cop_thief/gui/app.py` (green):
  - Wires `BoardView` + `InfoPanel` + `ScreenshotCapture`
  - Subscribes to `game_session.on_state_change`
  - Starts tkinter main loop in separate thread
  - Exits cleanly when game ends
- [ ] Headless mode: if `gui.enabled = false`, skip all GUI init
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 5. Manual Validation

- [ ] Run with GUI: `uv run python src/main.py --gui`
  → Window opens, grid displays correctly
- [ ] Verify cop (blue) and thief (red) visible at correct positions
- [ ] Place a barrier during game → gray cell appears
- [ ] Verify screenshot files created in `assets/screenshots/`
- [ ] Check all 5 trigger screenshots exist after game ends

---

## 6. Phase 5 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] GUI runs and screenshots save correctly
- [ ] Headless mode unchanged
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 5 — tkinter GUI + screenshot capture"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done`
