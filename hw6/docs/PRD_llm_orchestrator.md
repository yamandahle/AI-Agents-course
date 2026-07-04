# PRD — LLM Orchestrator

**Mechanism:** LLM Orchestrator (MCP Client)  
**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft

---

## 1. Purpose

The orchestrator is the MCP **Client** — it drives the full game loop.
For each agent's turn it: fetches the observation via MCP tool call, optionally
injects a Q-table tactical hint, constructs the LLM prompt, calls the LLM
(via ApiGatekeeper), parses the chosen action, and executes it via MCP tool call.

The LLM lives here — not inside the MCP servers.

---

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Game loop | Run turns in order: Thief → Cop, repeat until sub-game ends |
| Observation fetch | Call `get_observation` MCP tool for current agent |
| Prompt construction | Build system + user prompt with game state, rules, Q-hint |
| Q-table hint injection | If `q_table.enabled`, append top-action hint to prompt |
| LLM call | Send prompt to Ollama/API via ApiGatekeeper |
| Action parsing | Extract action (direction or place_barrier) from LLM response |
| MCP tool dispatch | Call `make_move` or `place_barrier` based on parsed action |
| Message exchange | Call `send_message` with LLM-generated natural-language message |
| Retry logic | On invalid action parse, re-prompt LLM up to max_retries |
| Sub-game handoff | Signal game engine on sub-game end; start next sub-game |
| Report trigger | After 6 sub-games, trigger Gmail report sender |

---

## 3. Turn Flow (per agent per turn)

```
1. get_observation(agent_id)          ← MCP tool call
2. q_table.get_hint(state)            ← if q_table.enabled (local call)
3. build_prompt(observation, hint)    ← prompt construction
4. llm.complete(prompt)               ← ApiGatekeeper → Ollama
5. parse_action(llm_response)         ← extract Action + message text
6. send_message(message)              ← MCP tool call
7. dispatch_action(action)            ← make_move or place_barrier MCP tool
8. check_terminal()                   ← game engine SDK call
```

---

## 4. Prompt Structure

### System prompt (set once per sub-game)

```
You are the {agent_role} agent in a pursuit game on a {R}x{C} grid.
Your goal: {cop_goal | thief_goal}.

Rules:
- You move one cell per turn in 8 directions: N, NE, E, SE, S, SW, W, NW.
{cop_only: - You may place_barrier on your current cell instead of moving
           (max {max_barriers} per sub-game, {remaining} remaining).}
- You win if: {win_condition}.
- You MUST first send a natural-language message to your opponent,
  then declare your action.

Communication: Your message may be truthful, vague, or deceptive.
Never reveal raw coordinates. Speak naturally.
```

### User prompt (built each turn)

```
Current observation:
- Your position: row {r}, col {c}
- Move number: {t} of {max_moves}
- Barriers on board: {barrier_list_in_natural_language}
- Opponent: {visible: "at approximately {direction}, {distance} cells away"
            | hidden: "position unknown"}
- Opponent's last message: "{last_message}"
{if q_table.enabled:
- Tactical hint: {hint_text}
}

Respond in this exact format:
MESSAGE: <your natural-language message to opponent>
ACTION: <one of: N, NE, E, SE, S, SW, W, NW, BARRIER>
```

### Response parsing

Expected format enforced via regex. On parse failure: retry up to
`llm.max_retries` times (from config) with an error correction prompt.
If all retries fail: pick a random valid action (fallback, logged as warning).

---

## 5. Q-Table Integration

```python
class QTableAdvisor:
    def get_hint(self, cop_pos, thief_pos) -> str:
        """Returns natural-language hint or empty string if disabled."""
        state = self._encode_state(cop_pos, thief_pos)
        best_action = np.argmax(self.q_table[state])
        return f"Position analysis suggests moving {ACTION_NAMES[best_action]}."

    def update(self, state, action, reward, next_state, done):
        """Bellman update — called during training only, not during live games."""
```

The Q-table is pre-trained via `uv run python -m cop_thief.sdk.q_table.train`
before games start. The trained table is saved to `config/q_table.npy`.

---

## 6. ApiGatekeeper Usage

All LLM calls go through `ApiGatekeeper`:

```python
response = gatekeeper.call(
    provider="ollama",
    endpoint="/api/chat",
    payload={"model": config.llm.model, "messages": prompt_messages},
    timeout=config.llm.timeout_seconds,
)
```

ApiGatekeeper handles: rate limits, queuing, retries, call logging.

---

## 7. Config Parameters Used

```
llm.provider
llm.model
llm.base_url
llm.timeout_seconds
llm.max_retries
q_table.enabled
q_table.alpha / gamma / epsilon / training_episodes
game.max_moves
game.max_barriers
vision.cop_vision_radius / thief_vision_radius
```

---

## 8. Test Plan

| Test | Type | Description |
|------|------|-------------|
| `test_prompt_contains_observation` | unit | Prompt includes position, move counter |
| `test_prompt_hides_opponent` | unit | Out-of-radius opponent → "unknown" in prompt |
| `test_prompt_includes_q_hint` | unit | q_table.enabled=True → hint in prompt |
| `test_parse_valid_action` | unit | "ACTION: NE" parses to Direction.NE |
| `test_parse_barrier_action` | unit | "ACTION: BARRIER" parses to place_barrier |
| `test_parse_invalid_retries` | unit | Bad LLM response triggers retry |
| `test_parse_all_retries_fail` | unit | Fallback to random valid action |
| `test_full_turn_cycle` | integration | Full turn: observe → LLM → act (mocked LLM) |
| `test_six_sub_game_loop` | integration | Orchestrator completes 6 sub-games (mocked) |

All LLM calls are mocked in tests — no real Ollama required.

---

## 9. File Layout

```
src/cop_thief/orchestrator/
├── __init__.py
├── game_loop.py       # Main loop: runs turns, manages sub-games
├── prompt_builder.py  # Builds system + user prompts
├── action_parser.py   # Parses LLM text response to Action
└── mcp_client.py      # Thin wrapper around FastMCP client calls

src/cop_thief/sdk/q_table/
├── __init__.py
├── advisor.py         # QTableAdvisor (hint generation)
└── trainer.py         # Self-play training loop
```

Each file stays under 150 code lines.
