# TODO — Phase 1: Game Engine

**Dependency:** None — start here.  
**PRD:** [PRD_game_engine.md](PRD_game_engine.md)  
**Status:** [x] Done

---

## 1. Project Skeleton

- [x] Create directory structure:
  ```
  src/cop_thief/sdk/game_engine/
  src/cop_thief/sdk/
  tests/unit/
  tests/integration/
  config/
  assets/screenshots/
  results/
  notebooks/
  ```
- [x] Create `pyproject.toml` with all dependencies (see PLAN.md §5)
- [x] Run `uv sync` — verify no errors
- [x] Create `src/cop_thief/version.py` → `version = "1.00"`
- [x] Create `config/config.json` with all defaults (see PRD.md §10)
- [x] Create `.env.example` with dummy values
- [x] Create `.gitignore` (include `.env`, `credentials.json`, `token.json`, `*.npy`, `__pycache__`)
- [x] Create empty `docs/PROMPTS.md`

---

## 2. Board (TDD)

- [x] Write `tests/unit/test_board.py` FIRST (red):
  - `test_move_all_8_directions`
  - `test_move_blocked_by_barrier`
  - `test_move_out_of_bounds`
  - `test_barrier_placed_on_current_cell`
  - `test_barrier_limit_exceeded`
  - `test_board_to_dict_serializes`
- [x] Implement `src/cop_thief/sdk/game_engine/board.py` (green):
  - `CellState` enum
  - `Direction` enum with (dr, dc) deltas
  - `Action` dataclass
  - `GameBoard` class
- [x] Refactor if needed — keep file ≤ 150 code lines
- [x] `uv run ruff check src/cop_thief/sdk/game_engine/board.py` → 0 violations

---

## 3. Observation Engine (TDD)

- [x] Write `tests/unit/test_observation.py` FIRST (red):
  - `test_own_position_always_visible`
  - `test_barriers_always_visible`
  - `test_opponent_visible_within_radius`
  - `test_opponent_hidden_outside_radius`
  - `test_chebyshev_distance_diagonal`
  - `test_message_included_in_observation`
- [x] Implement `src/cop_thief/sdk/game_engine/observation.py` (green):
  - `Observation` dataclass
  - `ObservationEngine` class
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 4. Sub-Game (TDD)

- [x] Write `tests/unit/test_sub_game.py` FIRST (red):
  - `test_cop_wins_by_capture`
  - `test_thief_wins_by_survival`
  - `test_turn_order_thief_first`
  - `test_invalid_move_raises_error`
  - `test_step_result_contains_observations`
  - `test_sub_game_result_scores_correct`
- [x] Implement `src/cop_thief/sdk/game_engine/sub_game.py` (green):
  - `StepResult` dataclass
  - `SubGameResult` dataclass
  - `SubGame` class
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 5. Game Session (TDD)

- [x] Write `tests/integration/test_game_session.py` FIRST (red):
  - `test_six_valid_sub_games_complete`
  - `test_crashed_sub_game_is_rerun`
  - `test_scores_accumulate_correctly`
  - `test_game_result_has_sub_game_log`
- [x] Implement `src/cop_thief/sdk/game_engine/game_session.py` (green):
  - `GameResult` dataclass
  - `GameSession` class
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 6. Phase 1 Sign-off

- [x] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [x] `uv run ruff check .` → 0 violations
- [x] Manual test: run a 2×1 sub-game with hardcoded moves → correct result
- [x] All files have module + class + function docstrings
- [x] No hardcoded values — all params from config.json
- [x] Commit: `git commit -m "ex06: phase 1 — game engine SDK"`
- [x] Push to `yamandahle-hw6`
- [x] Update [TODO.md](TODO.md) phase status to `[x] Done`
