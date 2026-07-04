# PRD — Game Engine

**Mechanism:** Game Engine  
**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft

---

## 1. Purpose

The Game Engine is the authoritative source of truth for all board state.
It enforces game rules, generates per-agent observations (fog of war), detects
win conditions, and manages the sub-game and full-game lifecycle.
It lives entirely inside `src/cop_thief/sdk/game_engine/` — no GUI, MCP, or
LLM code touches it directly.

---

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Board representation | N×M grid with cell states (empty, barrier, cop, thief) |
| Move validation | Reject out-of-bounds and barrier-blocked moves |
| Barrier placement | Cop places barrier on current cell; enforces max_barriers limit |
| Turn management | Thief moves first, then Cop; increment move counter |
| Win detection | Cop on Thief cell → cop_win; move_counter == max_moves → thief_win |
| Observation generation | Apply fog-of-war per agent using Chebyshev distance |
| Sub-game lifecycle | Initialize, run turns, return result with score |
| Full-game lifecycle | Run num_games valid sub-games; re-run crashed ones |
| Score accumulation | Accumulate cop/thief scores across all sub-games |

---

## 3. Key Classes and Interfaces

### `GameBoard`
```
GameBoard(rows, cols)
  .place_barrier(row, col) -> bool
  .move_agent(agent_id, direction) -> bool
  .get_cell(row, col) -> CellState
  .is_valid_move(agent_id, direction) -> bool
  .get_chebyshev_distance(pos1, pos2) -> int
  .to_dict() -> dict   # for serialization
```

### `ObservationEngine`
```
ObservationEngine(config)
  .get_observation(board, agent_id, message) -> Observation
    # Returns own_position, barriers, move_counter,
    # opponent_pos (null if outside vision radius), last_message
```

### `SubGame`
```
SubGame(config)
  .reset(cop_start, thief_start) -> None
  .step(cop_action, thief_action) -> StepResult
  .is_terminal() -> bool
  .get_result() -> SubGameResult   # winner, scores, moves_played
```

### `GameSession`
```
GameSession(config)
  .run() -> GameResult   # orchestrates num_games sub-games
  .get_scores() -> dict  # {"cop": int, "thief": int}
  .get_sub_game_log() -> list[SubGameResult]
```

---

## 4. Observation Structure

```python
@dataclass
class Observation:
    agent_id: str          # "cop" or "thief"
    own_position: tuple    # (row, col)
    barriers: list[tuple]  # [(row, col), ...]
    move_counter: int
    opponent_pos: tuple | None   # None if outside vision radius
    last_message: str | None     # opponent's last natural-language message
```

Fog-of-war rule: `opponent_pos` is set only when
`chebyshev(own_pos, opponent_pos) <= vision_radius[agent_id]`

---

## 5. Action Encoding

```python
class Direction(Enum):
    N  = (-1, 0)
    NE = (-1, 1)
    E  = (0,  1)
    SE = (1,  1)
    S  = (1,  0)
    SW = (1, -1)
    W  = (0, -1)
    NW = (-1,-1)

class Action:
    move: Direction | None     # None means place_barrier
```

---

## 6. Config Parameters Used

```
grid.rows, grid.cols
game.max_moves
game.max_barriers
game.num_games
vision.cop_vision_radius
vision.thief_vision_radius
scoring.cop_win / cop_loss / thief_win / thief_loss
```

---

## 7. Error Handling

- Invalid move (out of bounds, blocked) → raise `InvalidMoveError`; caller must request a new action
- Crashed sub-game (LLM timeout, MCP failure) → `SubGameResult.crashed = True`; `GameSession` re-runs it
- Barrier limit exceeded → raise `BarrierLimitError`

---

## 8. Test Plan

| Test | Type | Description |
|------|------|-------------|
| `test_move_all_directions` | unit | Valid moves in all 8 directions |
| `test_move_blocked_by_barrier` | unit | Blocked move raises InvalidMoveError |
| `test_move_out_of_bounds` | unit | OOB move raises InvalidMoveError |
| `test_barrier_limit` | unit | 6th barrier raises BarrierLimitError |
| `test_cop_win_detection` | unit | Cop landing on thief triggers cop_win |
| `test_thief_win_detection` | unit | Reaching max_moves triggers thief_win |
| `test_fog_of_war_visible` | unit | Opponent within radius → pos returned |
| `test_fog_of_war_hidden` | unit | Opponent outside radius → None returned |
| `test_full_sub_game` | integration | Sub-game runs to completion with valid result |
| `test_six_sub_games` | integration | GameSession returns 6 valid sub-game results |

---

## 9. File Layout

```
src/cop_thief/sdk/game_engine/
├── __init__.py
├── board.py          # GameBoard, CellState, Direction, Action
├── observation.py    # ObservationEngine, Observation dataclass
├── sub_game.py       # SubGame, StepResult, SubGameResult
└── game_session.py   # GameSession, GameResult
```

Each file stays under 150 code lines.
