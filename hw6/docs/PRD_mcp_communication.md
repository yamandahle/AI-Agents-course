# PRD — MCP Communication

**Mechanism:** MCP Servers (Cop & Thief)  
**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft

---

## 1. Purpose

Two independent FastMCP servers — one for the Cop agent, one for the Thief agent.
Each server exposes tools that the orchestrator (MCP Client) calls.
The servers contain **no LLM logic and no game decisions** — they are pure
tool-exposure layers that delegate to the SDK.

---

## 2. Architecture Principle

```
Orchestrator (MCP Client)
    │
    ├──► cop_server  (port 8001)   exposes: get_observation, send_message, make_move, place_barrier
    └──► thief_server (port 8002)  exposes: get_observation, send_message, make_move
```

- Servers run as separate processes.
- Ports come from `config.mcp.cop_port` and `config.mcp.thief_port`.
- Authentication: token-based (`Authorization: Bearer <token>` header).
- Token stored in `.env`, never in code or config.

---

## 3. Tool Definitions

### Shared tools (both servers)

#### `get_observation() -> dict`
Returns the agent's current observation from the game engine.
```json
{
  "own_position": [2, 3],
  "barriers": [[1, 1], [3, 3]],
  "move_counter": 7,
  "opponent_pos": [2, 4],
  "last_message": "I'm heading north, don't follow me."
}
```
`opponent_pos` is `null` when opponent is outside vision radius.

#### `send_message(message: str) -> dict`
Agent sends a natural-language message to the opponent.
Message is stored; delivered in opponent's next `get_observation` call.
```json
{ "status": "ok" }
```
- Enforces `communication.max_message_chars` limit.
- Raises `MessageTooLongError` if exceeded.

#### `make_move(direction: str) -> dict`
Agent moves one cell in the given direction.
```json
{ "status": "ok", "new_position": [2, 4] }
```
- `direction` must be one of: `"N", "NE", "E", "SE", "S", "SW", "W", "NW"`.
- Raises `InvalidMoveError` if blocked or out of bounds.

### Cop-only tool

#### `place_barrier() -> dict`
Cop places a barrier on its **current** cell instead of moving.
```json
{ "status": "ok", "barrier_placed_at": [2, 3], "barriers_remaining": 4 }
```
- Raises `BarrierLimitError` if max_barriers already reached.

---

## 4. Server Lifecycle

```
startup:
  1. Load config (grid, ports, token)
  2. Instantiate shared GameBoard reference (injected by orchestrator)
  3. Register FastMCP tools
  4. Start HTTP server on configured port

per-request:
  1. Validate Bearer token
  2. Route to SDK method
  3. Return JSON result or raise typed error

shutdown:
  1. Graceful close on SIGTERM
```

---

## 5. Error Responses

All errors return structured JSON (never plain text):
```json
{ "error": "InvalidMoveError", "detail": "Cell (3,3) is a barrier." }
```

| Error class | HTTP status | Cause |
|-------------|------------|-------|
| `InvalidMoveError` | 422 | Move blocked or out of bounds |
| `BarrierLimitError` | 422 | max_barriers already placed |
| `MessageTooLongError` | 422 | Message exceeds char limit |
| `AuthError` | 401 | Missing or invalid token |
| `GameNotStartedError` | 409 | Tool called before game initialized |

---

## 6. Authentication

- Token generated once at game startup, stored in `.env` as `MCP_AUTH_TOKEN`.
- Both servers read the same token.
- Orchestrator sets `Authorization: Bearer <token>` on every request.
- Token is never logged.

---

## 7. Config Parameters Used

```
mcp.cop_port
mcp.thief_port
communication.max_message_chars
```

Token: from `.env` (not config.json).

---

## 8. Test Plan

| Test | Type | Description |
|------|------|-------------|
| `test_get_observation_visible` | unit | Returns opponent pos when in radius |
| `test_get_observation_hidden` | unit | Returns null when out of radius |
| `test_make_move_valid` | unit | Valid direction updates position |
| `test_make_move_blocked` | unit | Blocked move returns 422 |
| `test_place_barrier_ok` | unit | Barrier placed, count decrements |
| `test_place_barrier_limit` | unit | 6th barrier returns 422 |
| `test_send_message_ok` | unit | Message stored for delivery |
| `test_send_message_too_long` | unit | Over-limit message returns 422 |
| `test_auth_missing_token` | unit | No token returns 401 |
| `test_both_servers_run` | integration | Both servers start and respond on correct ports |
| `test_full_turn_pipeline` | integration | Observation → message → move completes round-trip |

All tests mock the game engine SDK — no real board state needed.

---

## 9. File Layout

```
src/cop_thief/mcp/
├── __init__.py
├── cop_server.py     # FastMCP app for Cop (tools + auth middleware)
├── thief_server.py   # FastMCP app for Thief (tools + auth middleware)
└── tools.py          # Shared tool implementations (delegates to SDK)
```

Each file stays under 150 code lines.
