# PRD — Cop & Thief: Dual AI Agents via MCP (EX06)

**Version:** 1.0  
**Date:** 2026-07-03  
**Authors:** [Team members]  
**Status:** Draft — awaiting review

---

## 1. Project Overview

A two-agent pursuit game where a Cop agent chases a Thief agent on a 2D grid.
Each agent is powered by an LLM and communicates **only in free natural language** —
never raw coordinates. Agents are orchestrated via MCP (Model Context Protocol):
each has its own FastMCP server that exposes game tools; the LLM lives in the
orchestrator **client**, not in the servers.

The primary deliverable is a fully autonomous pipeline where both agents play
6 sub-games end-to-end, then the Cop agent emails a structured JSON report to
the lecturer with no human intervention.

---

## 2. Formal Model: Dec-POMDP

The game is modelled as a **Decentralized Partially Observable Markov Decision
Process**:

```
⟨ n, S, {Aᵢ}, P, R, {Ωᵢ}, O, γ ⟩
```

| Element | Definition | Game mapping |
|---------|-----------|--------------|
| **n** | Number of agents | 2 — Cop (i=0), Thief (i=1) |
| **S** | Joint state space | All combinations of (cop_pos, thief_pos, barrier_set, move_counter) on an N×M grid |
| **{Aᵢ}** | Action sets per agent | 8 directional moves (N/NE/E/SE/S/SW/W/NW); Cop additionally has "place_barrier" on current cell |
| **P** | Transition function | Deterministic: new positions given joint actions; barrier cells block movement |
| **R** | Reward function | Per sub-game: cop_win → (Cop +20, Thief +5); thief_win → (Thief +10, Cop +5) |
| **{Ωᵢ}** | Observation spaces | Each agent observes: own position (always), all barriers (always), move counter (always), opponent position **only if** Chebyshev distance ≤ vision_radius_i (from config) |
| **O** | Observation function | Applies fog-of-war filter per agent; when opponent is outside radius, opponent field is null |
| **γ** | Discount factor | 0.95 (near-1 for long-horizon sub-games; configurable) |

### Why Dec-POMDP and not MDP?

- **Decentralized**: each agent acts independently with no shared internal state
- **Partially observable**: each agent has its own local view; neither sees the full board
- **Natural language messages** pass between agents each turn but are unconstrained — an agent may tell the truth, be vague, or deliberately deceive

---

## 3. Game Mechanics

### 3.1 Structure

- **Sub-game**: one pursuit episode, max `max_moves` turns (default 25). Thief moves first each turn, then Cop.
- **Full game**: exactly `num_games` valid sub-games (default 6). Crashed sub-games are re-run until 6 valid ones complete.
- **Starting positions**: random or strategy-based (from config). Cop and Thief start on distinct cells.

### 3.2 Actions

| Agent | Available actions |
|-------|-----------------|
| Thief | Move to any of 8 adjacent cells (if in bounds and not a barrier) |
| Cop | Move to any of 8 adjacent cells **OR** place a barrier on current cell |

- Barriers placed by Cop become permanently impassable for **both** agents.
- Cop may place at most `max_barriers` barriers per sub-game (default 5).
- Thief cannot place barriers.

### 3.3 Win conditions

| Outcome | Trigger | Cop score | Thief score |
|---------|---------|-----------|-------------|
| Cop wins sub-game | Cop lands exactly on Thief's cell | 20 | 5 |
| Thief wins sub-game | Thief survives all `max_moves` turns | 5 | 10 |

### 3.4 Scoring

- Scores accumulate across all 6 sub-games.
- Maximum possible score for a team: Cop 90 pts (3 wins × 20 + 3 losses × 5 is not max; max is 6 × 20 = 120); Thief max is 6 × 10 = 60.
- Minimum possible score: Cop 30 (6 × 5), Thief 30 (6 × 5).

### 3.5 Gradual sanity check grids (from assignment)

To validate integration progressively before running the full 5×5 game:

| Stage | Grid | Purpose |
|-------|------|---------|
| 1 | 2×1 | Basic algorithmic pipeline and message passing |
| 2 | 3×2 or 2×3 | Coordination mechanisms, hyper-parameter failure detection |
| 3 | 4×3 or 3×4 | Effect of vision radius and initial starting distance |
| 4 | 5×5 | Final test, graph generation, full game analysis |

---

## 4. Fog-of-War Observability Model

Each agent's observation at turn t is constructed by the game engine as follows:

```
observation_i(t) = {
    "own_position":   (row, col),          # always truthful
    "barriers":       [(r,c), ...],        # full barrier set, always visible
    "move_counter":   t,                   # always visible
    "opponent_pos":   (row, col) | null,   # visible only if Chebyshev(own, opp) <= vision_radius_i
    "message":        "<natural language>" # last message from opponent (unconstrained)
}
```

**Chebyshev distance** between cells (r1,c1) and (r2,c2):
```
d = max(|r1-r2|, |c1-c2|)
```

Vision radii are **per-agent** and come from config:
- `cop_vision_radius` — how far the Cop can see
- `thief_vision_radius` — how far the Thief can see

These are the primary experiment variables (see Section 8).

---

## 5. Agent Architecture

### 5.1 MCP Architecture

```
┌─────────────────────────────────────────────┐
│            Orchestrator (MCP Client)        │
│   ┌───────────┐          ┌───────────────┐  │
│   │  LLM      │◄────────►│  Game Engine  │  │
│   │ (Ollama)  │          │  (SDK layer)  │  │
│   └───────────┘          └───────────────┘  │
│         │                                   │
│    Tool calls                               │
└────┬────────────────────────────────────────┘
     │
     ├──► MCP Server (Cop)    — exposes tools only
     └──► MCP Server (Thief)  — exposes tools only
```

**Critical principle:** The LLM is NOT inside the MCP server. The MCP servers
only expose tools (get_observation, send_message, make_move, place_barrier).
The orchestrator calls those tools and feeds results to the LLM to decide.

### 5.2 LLM Approach (Approach 3 — Hybrid/Local)

During development: Ollama runs locally; both MCP servers and the orchestrator
run on localhost at separate ports. No external exposure needed.

The orchestrator calls Ollama at `localhost:11434`. MCP servers expose tools
only — they contain no LLM logic.

Config key `llm.provider` can switch between `"ollama"` and `"openai"` with
no code changes.

### 5.3 Q-Table Tactical Advisor (optional, recommended)

The assignment recommends a simple Tabular Q-Learning layer (Section 8 of spec).
We implement it as a **tactical advisor** injected into the LLM prompt:

1. A Q-table trains during self-play on the 5×5 game environment.
2. At each turn, the Q-table's top-1 recommended action is formatted as a
   natural-language hint: *"Position analysis suggests moving North-East."*
3. The hint is appended to the LLM system prompt.
4. The LLM retains full decision authority — it may follow or override the hint.

**Q-table state:** `(cop_row, cop_col, thief_row, thief_col)` — 25×25 = 625 states.  
**Actions:** 8 directions + place_barrier = 9 actions.  
**Update rule (Bellman equation):**
```
Q(s,a) ← Q(s,a) + α [ r + γ · max_a' Q(s',a') − Q(s,a) ]
```
Default hyperparameters (all in config): `alpha=0.1`, `gamma=0.95`, `epsilon=0.1`.

The Q-table advisor can be toggled via `q_table.enabled` in config — enabling
the on/off experiment dimension.

---

## 6. Communication Protocol

- Agents communicate ONLY in free natural language messages.
- No raw coordinates, no structured data, no fixed vocabulary.
- Messages may be truthful, vague, or deliberately deceptive — all are legal.
- Each agent receives the opponent's last message as part of its observation.
- Message length is bounded by `communication.max_message_chars` in config.

---

## 7. External Integrations

### 7.1 Gmail Report (mandatory)

After 6 sub-games complete, the **Cop agent** automatically sends one email:
- **To:** `rmisegal+uoh26b@gmail.com` (from config — never hardcoded)
- **Body:** JSON-only, no free text, structured per the assignment spec (Section 9)
- **Auth:** OAuth 2.0 with Desktop client type; scopes `gmail.modify` + `calendar`
- **Files:** `credentials.json` + `token.json` — both git-ignored

JSON report schema (Internal Game):
```json
{
  "group_name": "...",
  "students": ["name1", "name2"],
  "github_repo": "...",
  "cop_mcp_url": "...",
  "thief_mcp_url": "...",
  "timezone": "Asia/Jerusalem",
  "sub_games": [...],
  "totals": { "cop": 0, "thief": 0 }
}
```

### 7.2 ApiGatekeeper

All external calls (Ollama/LLM API, Gmail API) are routed through a central
`ApiGatekeeper`:
- Rate limits from `config/rate_limits.json`
- Queue instead of reject on limit hit
- Automatic retries with exponential backoff
- Full call log (timestamp, endpoint, latency, success/fail)

---

## 8. Experiments Plan

All experiments are driven **exclusively by config changes** — zero code
modifications between runs.

### 8.1 Experiment dimensions

| Dimension | Values | What it tests |
|-----------|--------|--------------|
| `cop_vision_radius` | 0, 1, 2, 4 (full) | How much Cop visibility affects capture rate |
| `thief_vision_radius` | 0, 1, 2, 4 (full) | How much Thief visibility affects escape rate |
| `q_table.enabled` | true, false | Whether Q-table advisor improves agent performance |
| Thief prompt style | honest, vague, deceptive | Effect of communication strategy on outcomes |
| Initial placement | random, max_distance | Starting distance effect on sub-game length |

### 8.2 Planned experiment cases

| Case | cop_vision | thief_vision | q_table | Thief style | Hypothesis |
|------|-----------|--------------|---------|-------------|-----------|
| A (baseline) | 2 | 2 | off | honest | Balanced — 50/50 expected |
| B (blind cop) | 0 | 2 | off | honest | Thief dominates |
| C (full visibility) | 4 | 4 | off | honest | Cop dominates |
| D (RL cop) | 2 | 2 | on | honest | Q-table improves cop win rate |
| E (deceptive thief) | 2 | 2 | off | deceptive | Deception benefits Thief |
| F (close start) | 2 | 2 | off | honest | Cop wins faster |
| G (max distance) | 2 | 2 | off | honest | Thief wins more often |

Each case runs 1 full game (6 sub-games). Results recorded to `results/`.

### 8.3 Outputs and screenshots

For each experiment case:

- **Score table** — cop_total, thief_total, sub-game breakdown
- **Win-rate bar chart** — cop wins vs thief wins across cases
- **Capture turn histogram** — distribution of which turn cop captured thief
- **Communication log** — agent messages per sub-game (saved to `results/`)
- **Screenshots** — captured via GUI at key moments:
  - Game start (initial board)
  - First barrier placed
  - First capture or 25-move timeout
  - Final scoreboard
  - Screenshots saved to `assets/screenshots/<case_name>/`

All graphs and analysis collected in `notebooks/experiments.ipynb`.

---

## 9. Success Criteria

### 9.1 Functional

| Criterion | Pass condition |
|-----------|---------------|
| Agents communicate | Each turn both agents exchange at least one natural-language message |
| Cop wins at least once | In any 6-game run, Cop captures Thief ≥ 1 time |
| Thief survives at least once | In any 6-game run, Thief reaches 25 moves ≥ 1 time |
| Full pipeline runs autonomously | 6 sub-games complete with zero human interaction |
| Email report sent | Lecturer receives JSON report after game ends |
| Config-driven | Changing `config.json` changes behavior with zero code edits |

### 9.2 Quality (graded)

| Criterion | Target |
|-----------|--------|
| Test coverage | ≥ 85% (enforced via `fail_under = 85`) |
| Ruff violations | 0 |
| Lines per code file | ≤ 150 (comments/blanks excluded) |
| Docstrings | Every function, class, module |
| No hardcoded params | All game params from `config/config.json` |
| No secrets in code | `.env` + `.env-example` pattern |

---

## 10. Configuration Parameters

All parameters in `config/config.json`. No hardcoded values anywhere in code.

```json
{
  "version": "1.0",
  "grid": { "rows": 5, "cols": 5 },
  "game": {
    "max_moves": 25,
    "num_games": 6,
    "max_barriers": 5
  },
  "scoring": {
    "cop_win": 20,
    "thief_win": 10,
    "cop_loss": 5,
    "thief_loss": 5
  },
  "vision": {
    "cop_vision_radius": 2,
    "thief_vision_radius": 2
  },
  "q_table": {
    "enabled": true,
    "alpha": 0.1,
    "gamma": 0.95,
    "epsilon": 0.1,
    "training_episodes": 10000
  },
  "llm": {
    "provider": "ollama",
    "model": "llama3",
    "base_url": "http://localhost:11434",
    "timeout_seconds": 30
  },
  "mcp": {
    "cop_port": 8001,
    "thief_port": 8002
  },
  "communication": {
    "max_message_chars": 300
  },
  "gmail": {
    "recipient": "rmisegal+uoh26b@gmail.com",
    "credentials_file": "credentials.json",
    "token_file": "token.json"
  },
  "reporting": {
    "group_name": "",
    "github_repo": "",
    "timezone": "Asia/Jerusalem"
  }
}
```

---

## 11. Project Structure

```
hw6/
├── src/
│   └── cop_thief/
│       ├── sdk/              # All business logic (game engine, agents, Q-table)
│       ├── mcp/              # MCP server definitions (cop_server.py, thief_server.py)
│       ├── orchestrator/     # MCP client + LLM integration
│       ├── gui/              # Visual board (calls SDK only)
│       ├── gmail/            # Gmail report sender
│       └── version.py        # version = "1.00"
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── PRD.md                # this file
│   ├── PLAN.md               # next
│   ├── TODO.md               # next
│   ├── PRD_game_engine.md
│   ├── PRD_mcp_communication.md
│   ├── PRD_llm_orchestrator.md
│   ├── PRD_gui.md
│   ├── PRD_gmail_report.md
│   ├── PRD_experiments.md
│   └── PROMPTS.md            # prompt log (graded)
├── config/
│   ├── config.json
│   └── rate_limits.json
├── results/                  # experiment outputs
├── notebooks/
│   └── experiments.ipynb
├── assets/
│   └── screenshots/
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

---

## 12. Out of Scope

| Item | Reason |
|------|--------|
| Inter-group bonus competition | Not implemented (optional, future) |
| Deep RL / neural networks | Tabular Q-table is sufficient and assignment-specified |
| Q-table replacing the LLM | LLM must make final decisions (core architecture requirement) |
| Calendar API | Only Gmail is required for report |
| Cloud deployment | Approach 3 (local) for this submission |

---

## 13. Open Questions (to resolve in PLAN.md)

1. Which Ollama model? (`llama3`, `mistral`, or `gemma2`) — affects prompt quality
2. Q-table state representation: include barrier cells in state or ignore? (state space size tradeoff)
3. GUI framework: `tkinter` (no install) vs `pygame` (nicer visuals)?
4. Screenshot automation: manual captures or automated via `PIL.ImageGrab`?
5. Thief messaging prompts: how to instruct the LLM to be deceptive without hardcoding specific lies?
