# TODO — Phase 3: Orchestrator + LLM

**Dependency:** Phase 2 complete. Ollama running locally with llama3 pulled.  
**PRD:** [PRD_llm_orchestrator.md](PRD_llm_orchestrator.md)  
**Status:** [ ] Not started

---

## 0. Prerequisite

- [ ] Ollama installed: https://ollama.com
- [ ] Model pulled: `ollama pull llama3`
- [ ] Ollama serving: `ollama serve` (runs on localhost:11434)
- [ ] Verify: `curl http://localhost:11434/api/tags` returns model list

---

## 1. ApiGatekeeper (TDD)

- [ ] Create `config/rate_limits.json`:
  ```json
  { "version": "1.0", "ollama": {"calls_per_minute": 30, "max_retries": 3} }
  ```
- [ ] Write `tests/unit/test_api_gatekeeper.py` FIRST (red):
  - `test_call_succeeds_on_first_try`
  - `test_call_retries_on_failure`
  - `test_call_raises_after_max_retries`
  - `test_call_is_logged`
- [ ] Implement `src/cop_thief/api_gatekeeper.py` (green)
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 2. Prompt Builder (TDD)

- [ ] Write `tests/unit/test_prompt_builder.py` FIRST (red):
  - `test_system_prompt_contains_agent_role`
  - `test_user_prompt_contains_own_position`
  - `test_user_prompt_hides_opponent_when_null`
  - `test_user_prompt_shows_opponent_when_visible`
  - `test_user_prompt_contains_move_counter`
  - `test_cop_prompt_mentions_barrier_option`
  - `test_thief_prompt_has_no_barrier_mention`
  - `test_q_hint_included_when_enabled`
  - `test_q_hint_absent_when_disabled`
- [ ] Implement `src/cop_thief/orchestrator/prompt_builder.py` (green)
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 3. Action Parser (TDD)

- [ ] Write `tests/unit/test_action_parser.py` FIRST (red):
  - `test_parse_direction_north`
  - `test_parse_all_8_directions`
  - `test_parse_barrier_action`
  - `test_parse_case_insensitive`
  - `test_parse_invalid_returns_none`
  - `test_parse_message_extracted`
- [ ] Implement `src/cop_thief/orchestrator/action_parser.py` (green)
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 4. MCP Client (TDD)

- [ ] Write `tests/unit/test_mcp_client.py` FIRST (red):
  - `test_get_observation_calls_correct_server`
  - `test_make_move_sends_direction`
  - `test_send_message_posts_to_server`
  - `test_place_barrier_calls_cop_server`
- [ ] Implement `src/cop_thief/orchestrator/mcp_client.py` (green):
  - Thin wrapper around FastMCP HTTP calls
  - Reads URLs + token from config / .env
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 5. Game Loop (TDD)

- [ ] Write `tests/integration/test_game_loop.py` FIRST (red):
  - `test_thief_moves_before_cop`
  - `test_turn_calls_get_observation_then_move`
  - `test_loop_stops_on_cop_win`
  - `test_loop_stops_on_thief_win`
  - `test_six_sub_games_trigger_report`
  - `test_invalid_action_triggers_retry`
  - `test_all_retries_fail_triggers_fallback`
- [ ] Implement `src/cop_thief/orchestrator/game_loop.py` (green)
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 6. Entry Point

- [ ] Create `src/main.py`:
  - Parse CLI flags: `--gui`, `--case <name>`, `--headless`
  - Load config, start MCP servers, run orchestrator
  - Keep file ≤ 150 code lines

---

## 7. End-to-End Validation

- [ ] Sanity check 3×2 grid: `uv run python src/main.py --headless`
  → 6 sub-games complete, scores printed, no crash
- [ ] Sanity check 4×3 grid: adjust config, re-run
- [ ] Sanity check 5×5 grid (full game): `uv run python src/main.py --headless`
- [ ] Verify natural-language messages appear in output each turn
- [ ] Verify LLM retries on bad parse (force by watching logs)

---

## 8. Phase 3 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] Full 5×5 game runs end-to-end headlessly
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 3 — orchestrator + LLM game loop"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done`
