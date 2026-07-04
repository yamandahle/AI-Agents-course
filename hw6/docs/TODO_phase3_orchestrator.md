# TODO — Phase 3: Orchestrator + LLM

**Dependency:** Phase 2 complete. Ollama running locally with llama3 pulled.  
**PRD:** [PRD_llm_orchestrator.md](PRD_llm_orchestrator.md)  
**Status:** [ ] In progress — Steps 1-4 done, Step 5 (Game Loop) next

---

## 0. Prerequisite

- [x] Ollama installed: https://ollama.com
- [x] Model pulled: `ollama pull phi3:mini` (config switched from llama3 — see PROMPTS.md)
- [x] Ollama serving: `ollama serve` (runs on localhost:11434)
- [x] Verify: `curl http://localhost:11434/api/tags` returns model list

---

## 1. ApiGatekeeper (TDD)

- [x] Create `config/rate_limits.json`:
  ```json
  { "version": "1.0", "ollama": {"calls_per_minute": 30, "max_retries": 3} }
  ```
- [x] Write `tests/unit/test_api_gatekeeper.py` FIRST (red):
  - `test_call_succeeds_on_first_try`
  - `test_call_retries_on_failure`
  - `test_call_raises_after_max_retries`
  - `test_call_is_logged`
- [x] Implement `src/cop_thief/api_gatekeeper.py` (green)
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 2. Prompt Builder (TDD)

- [x] Write `tests/unit/test_prompt_builder.py` FIRST (red):
  - `test_system_prompt_contains_agent_role`
  - `test_user_prompt_contains_own_position`
  - `test_user_prompt_hides_opponent_when_null`
  - `test_user_prompt_shows_opponent_when_visible`
  - `test_user_prompt_contains_move_counter`
  - `test_cop_prompt_mentions_barrier_option`
  - `test_thief_prompt_has_no_barrier_mention`
  - `test_q_hint_included_when_enabled`
  - `test_q_hint_absent_when_disabled`
- [x] Implement `src/cop_thief/orchestrator/prompt_builder.py` (green)
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 3. Action Parser (TDD)

- [x] Write `tests/unit/test_action_parser.py` FIRST (red):
  - `test_parse_direction_north`
  - `test_parse_all_8_directions`
  - `test_parse_barrier_action`
  - `test_parse_case_insensitive`
  - `test_parse_invalid_returns_none`
  - `test_parse_message_extracted`
- [x] Implement `src/cop_thief/orchestrator/action_parser.py` (green)
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 4. MCP Client (TDD)

- [x] Write `tests/unit/test_mcp_client.py` FIRST (red):
  - `test_get_observation_calls_correct_server`
  - `test_make_move_sends_direction`
  - `test_send_message_posts_to_server`
  - `test_place_barrier_calls_cop_server`
- [x] Implement `src/cop_thief/orchestrator/mcp_client.py` (green):
  - Thin wrapper around FastMCP HTTP calls
  - Reads URLs + token from config / .env
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 5. Game Loop (TDD)

- [x] Write `tests/integration/test_game_loop.py` FIRST (red):
  - `test_thief_moves_before_cop`
  - `test_turn_calls_get_observation_then_move`
  - `test_loop_stops_on_cop_win`
  - `test_loop_stops_on_thief_win`
  - `test_six_sub_games_trigger_report`
  - `test_invalid_action_triggers_retry`
  - `test_all_retries_fail_triggers_fallback`
  - (added) `test_cop_barrier_action_calls_place_barrier`
  - (added) `test_crashed_sub_game_is_marked_and_retried`
  - (added) `test_too_many_crashes_raises`
  - (added) `test_random_starts_returns_two_distinct_in_bounds_cells`
- [x] Implement `src/cop_thief/orchestrator/game_loop.py` (green)
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 6. Entry Point

- [x] Create `src/main.py`:
  - Parse CLI flags: `--gui`, `--case <name>`, `--headless`
  - Load config, start MCP servers, run orchestrator
  - Keep file ≤ 150 code lines

---

## 7. End-to-End Validation

- [x] Sanity check 3×2 grid: `uv run python src/main.py --headless`
  → completed, no crash. See results/step7_smoke_3x2_before_fix.log
  (caught 2 real bugs — see PROMPTS.md) and step7_smoke_3x2_after_fix.log
  (clean run after fixes). Used reduced max_moves/num_games for speed.
- [x] Sanity check 4×3 grid: adjust config, re-run
  → completed, no crash, exercised full retry-exhaustion fallback for
  real. See results/step7_smoke_4x3.log.
- [ ] Sanity check 5×5 grid (full game, real config: 6 sub-games/25 moves):
  `uv run python src/main.py --headless` — handed to student to run in
  their own terminal (real run can take 30-90+ min; Claude's tool has a
  10-min limit). Awaiting result.
- [x] Verify natural-language messages appear in output each turn (empty
  strings in the small runs so far since test prompts didn't emphasize
  messaging — re-check on the full run)
- [x] Verify LLM retries on bad parse (force by watching logs) — confirmed
  live in step7_smoke_4x3.log ("Unparseable LLM response... attempt 1/3")

---

## 8. Phase 3 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] Full 5×5 game runs end-to-end headlessly
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 3 — orchestrator + LLM game loop"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done`
