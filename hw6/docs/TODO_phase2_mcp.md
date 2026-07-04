# TODO — Phase 2: MCP Servers

**Dependency:** Phase 1 complete.  
**PRD:** [PRD_mcp_communication.md](PRD_mcp_communication.md)  
**Status:** [x] Done

---

## 1. Auth & Config

- [x] Add `MCP_AUTH_TOKEN` to `.env.example` (dummy value)
- [x] Add real token to `.env` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- [x] Verify `config.json` has `mcp.cop_port = 8001` and `mcp.thief_port = 8002`

---

## 2. Shared Tools (TDD)

- [x] Write `tests/unit/test_mcp_tools.py` FIRST (red):
  - `test_get_observation_returns_correct_structure`
  - `test_get_observation_hides_opponent_outside_radius`
  - `test_make_move_valid_updates_position`
  - `test_make_move_blocked_returns_error`
  - `test_place_barrier_decrements_count`
  - `test_place_barrier_at_limit_returns_error`
  - `test_send_message_stores_for_delivery`
  - `test_send_message_too_long_returns_error`
- [x] Implement `src/cop_thief/mcp/tools.py` (green):
  - `get_observation_dict(ctx) -> dict`
  - `send_message_impl(ctx, message) -> dict`
  - `make_move_impl(ctx, direction) -> dict`
  - `place_barrier_impl(ctx) -> dict`
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 3. Cop Server (TDD)

- [x] Write `tests/unit/test_cop_server.py` FIRST (red):
  - `test_missing_token_returns_401`
  - `test_invalid_token_returns_401`
  - `test_valid_token_get_observation_succeeds`
  - `test_place_barrier_tool_exists`
- [x] Implement `src/cop_thief/mcp/cop_server.py` (green):
  - FastMCP app on `config.mcp.cop_port`
  - Auth via `check_auth` in `tools.py`
  - Register: `get_observation`, `send_message`, `make_move`, `place_barrier`
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 4. Thief Server (TDD)

- [x] Write `tests/unit/test_thief_server.py` FIRST (red):
  - `test_missing_token_returns_401`
  - `test_valid_token_get_observation_succeeds`
  - `test_place_barrier_tool_does_not_exist`
- [x] Implement `src/cop_thief/mcp/thief_server.py` (green):
  - FastMCP app on `config.mcp.thief_port`
  - Auth via `check_auth`
  - Register: `get_observation`, `send_message`, `make_move` (no place_barrier)
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 5. Integration Tests

- [x] Write `tests/integration/test_mcp_servers.py`:
  - `test_cop_server_has_place_barrier`
  - `test_thief_server_has_no_place_barrier`
  - `test_full_tool_round_trip` (observe → message → move)
  - `test_message_delivered_in_observation`
- [x] All integration tests pass with shared real SubGame

---

## 6. Phase 2 Sign-off

- [x] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [x] `uv run ruff check .` → 0 violations
- [x] All files have docstrings
- [x] Commit: `git commit -m "ex06: phase 2 — MCP servers"`
- [x] Push to `yamandahle-hw6`
- [x] Update [TODO.md](TODO.md) phase status to `[x] Done`
