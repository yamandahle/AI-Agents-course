# PRD — GUI (Graphical User Interface)

**Mechanism:** Visual Board Display  
**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft

---

## 1. Purpose

A real-time visual board that shows the game state as it plays out.
The GUI is a pure display layer — it calls the SDK only and contains
zero game logic. It is optional at runtime (the game can run headless via CLI).

---

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Board rendering | Draw N×M grid with color-coded cells |
| Agent display | Show Cop (blue) and Thief (red) icons at current positions |
| Barrier display | Shade barrier cells in dark gray |
| Score panel | Live cop/thief scores + sub-game number |
| Message panel | Last natural-language message from each agent |
| Turn indicator | Whose turn it is + move counter |
| Screenshot capture | Save PNG to `assets/screenshots/` at key moments |
| Headless mode | GUI disabled when `gui.enabled = false` in config |

---

## 3. Framework Decision

**Chosen: `tkinter`**

| Option | Pro | Con |
|--------|-----|-----|
| tkinter | Zero install, stdlib | Basic visuals |
| pygame | Smooth, nice sprites | Requires install |

`tkinter` is sufficient for a 5×5 grid display and requires no extra dependency.
If the team prefers `pygame`, change `gui.framework` in config — the SDK
interface stays identical.

---

## 4. Screen Layout

```
┌─────────────────────────────────────────┐
│  Sub-game: 3/6   Move: 12/25  Cop turn  │
├───────────────────┬─────────────────────┤
│                   │  SCORES             │
│   5×5  GRID       │  Cop:   45          │
│                   │  Thief: 30          │
│  [C] = Cop        ├─────────────────────┤
│  [T] = Thief      │  MESSAGES           │
│  [█] = Barrier    │  Cop: "I see you    │
│                   │  near the corner."  │
│                   │  Thief: "You're     │
│                   │  looking the wrong  │
│                   │  way."              │
└───────────────────┴─────────────────────┘
```

---

## 5. Screenshot Triggers

Screenshots are captured automatically at these moments:

| Trigger | Filename pattern |
|---------|-----------------|
| Sub-game start (initial board) | `<case>_sg<N>_start.png` |
| First barrier placed in sub-game | `<case>_sg<N>_barrier.png` |
| Cop captures Thief | `<case>_sg<N>_capture.png` |
| Thief survives 25 moves | `<case>_sg<N>_escape.png` |
| Final scoreboard after 6 sub-games | `<case>_final_score.png` |

All saved to `assets/screenshots/<experiment_case>/`.
Captured via `PIL.ImageGrab` (Pillow) — added as a dev dependency.

---

## 6. SDK Interface (GUI calls only these)

```python
# GUI subscribes to game state updates via callback:
game_session.on_state_change(callback: Callable[[GameState], None])

# GameState fields the GUI reads:
board: list[list[CellState]]
cop_position: tuple[int, int]
thief_position: tuple[int, int]
barriers: list[tuple[int, int]]
move_counter: int
sub_game_number: int
scores: dict[str, int]
last_messages: dict[str, str]
current_turn: str   # "cop" or "thief"
```

No game logic in GUI — it only reads `GameState` and renders it.

---

## 7. Config Parameters Used

```
grid.rows, grid.cols
gui.enabled           # true/false — headless mode
gui.cell_size_px      # pixel size per cell (default: 80)
gui.screenshot_dir    # path relative to project root
gui.framework         # "tkinter" or "pygame"
```

---

## 8. Test Plan

| Test | Type | Description |
|------|------|-------------|
| `test_gui_disabled_headless` | unit | gui.enabled=false → no window opened |
| `test_state_renders_cop_position` | unit | GameState with cop at (2,3) → correct cell highlighted |
| `test_barrier_cells_marked` | unit | Barrier set renders as blocked cells |
| `test_screenshot_saved` | unit | Screenshot trigger saves PNG to correct path |
| `test_score_panel_updates` | unit | Score change reflected in panel |

GUI tests use a headless renderer (mock canvas) — no real window required in CI.

---

## 9. File Layout

```
src/cop_thief/gui/
├── __init__.py
├── board_view.py      # Grid rendering (tkinter canvas or pygame surface)
├── info_panel.py      # Scores, messages, turn indicator
├── screenshot.py      # PIL.ImageGrab capture logic
└── app.py             # Main GUI app, wires board_view + info_panel + callbacks
```

Each file stays under 150 code lines.
