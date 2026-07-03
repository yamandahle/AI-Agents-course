# TODO — Phase 2: MCP Servers

**Dependency:** Phase 1 complete.  
**PRD:** [PRD_mcp_communication.md](PRD_mcp_communication.md)  
**Status:** [ ] Not started

---

## 1. Auth & Config

- [ ] Add `MCP_AUTH_TOKEN` to `.env.example` (dummy value)
- [ ] Add real token to `.env` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Verify `config.json` has `mcp.cop_port = 8001` and `mcp.thief_port = 8002`

---

## 2. Shared Tools (TDD)

- [ ] Write `tests/unit/test_mcp_tools.py` FIRST (red):
  - `test_get_observation_returns_correct_structure`
  - `test_get_observation_hides_opponent_outside_radius`
  - `test_make_move_valid_updates_position`
  - `test_make_move_blocked_returns_error`
  - `test_place_barrier_decrements_count`
  - `test_place_barrier_at_limit_returns_error`
  - `test_send_message_stores_for_delivery`
  - `test_send_message_too_long_returns_error`
- [ ] Implement `src/cop_thief/mcp/tools.py` (green):
  - `get_observation(agent_id, game_board, config) -> dict`
  - `send_message(agent_id, message, message_store, config) -> dict`
  - `make_move(agent_id, direction, game_board) -> dict`
  - `place_barrier(game_board, barrier_tracker) -> dict`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 3. Cop Server (TDD)

- [ ] Write `tests/unit/test_cop_server.py` FIRST (red):
  - `test_missing_token_returns_401`
  - `test_invalid_token_returns_401`
  - `test_valid_token_get_observation_succeeds`
  - `test_place_barrier_tool_exists`
- [ ] Implement `src/cop_thief/mcp/cop_server.py` (green):
  - FastMCP app on `config.mcp.cop_port`
  - Auth middleware (Bearer token check)
  - Register: `get_observation`, `send_message`, `make_move`, `place_barrier`
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 4. Thief Server (TDD)

- [ ] Write `tests/unit/test_thief_server.py` FIRST (red):
  - `test_missing_token_returns_401`
  - `test_valid_token_get_observation_succeeds`
  - `test_place_barrier_tool_does_not_exist`
- [ ] Implement `src/cop_thief/mcp/thief_server.py` (green):
  - FastMCP app on `config.mcp.thief_port`
  - Auth middleware
  - Register: `get_observation`, `send_message`, `make_move` (no place_barrier)
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 5. Integration Tests

- [ ] Write `tests/integration/test_mcp_servers.py`:
  - `test_both_servers_start_on_correct_ports`
  - `test_cop_server_has_place_barrier`
  - `test_thief_server_has_no_place_barrier`
  - `test_full_tool_round_trip` (observe → message → move)
- [ ] All integration tests pass with mocked game engine (no real board)

---

## 6. Phase 2 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] Manual test: start both servers, call `get_observation` via curl → correct JSON
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 2 — MCP servers"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done`
