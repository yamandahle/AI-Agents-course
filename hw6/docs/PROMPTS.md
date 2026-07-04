# PROMPTS — Decision Log (EX06)

This file logs all significant prompts and decisions made during development.
It is a graded requirement — update it after every meaningful decision.

---

## 2026-07-03 — Documentation Phase

**Decision:** Use Approach 3 (hybrid/local) for LLM architecture.  
**Reason:** No external exposure needed during development; swap to cloud via config.

**Decision:** Q-table as optional tactical advisor (injected into LLM prompt).  
**Reason:** Assignment recommends it (Section 8); keeps LLM as final decision-maker.

**Decision:** tkinter for GUI framework.  
**Reason:** Zero extra dependency (stdlib); sufficient for 5×5 grid display.

**Decision:** Q-table state = (cop_row, cop_col, thief_row, thief_col) only — no barriers.  
**Reason:** Keeps state space at 625 entries; barriers change per sub-game making Q-table unstable if included.

**Decision:** 7 experiment cases (A–G) covering vision radius, Q-table on/off, thief deception, initial placement.  
**Reason:** Shows diverse outcome scenarios required by assignment originality section.

---

## 2026-07-04 — Phase 2 Verification: MCP Servers Over Real HTTP

**Action:** Manually verified both MCP servers work over real network transport
(not just in-process), using a 3-terminal test:
- Terminal 1: `uv run python scripts/start_cop_demo.py` (cop server, port 8001)
- Terminal 2: `uv run python scripts/start_thief_demo.py` (thief server, port 8002)
- Terminal 3: `uv run python scripts/call_servers.py` (MCP client calling both)

**Result:** All tool calls succeeded (`list_tools`, `get_observation`,
`send_message`, `make_move`, `place_barrier`) — see
`assets/screenshots/mcp_3terminal_test.png` and full call log in
`results/mcp_demo.json`.

**Reason:** Confirms the client/server MCP architecture (LLM will live in the
orchestrator client, not in the servers) actually works across process
boundaries before building Phase 3 on top of it.

---

## Working agreement — screenshots & prompt logging

**Decision:** Claude proactively flags when a screenshot is worth capturing
at each milestone/update, and logs important prompts/decisions into this
file as they happen, rather than waiting to be asked.
**Reason:** Student requested this on 2026-07-04 to keep the graded prompt
log and visual evidence trail complete without manual reminders each time.

---

## 2026-07-04 — Merged Nagham's Gap Fixes + Phase 3 Started (Steps 1–4)

**Action:** Fetched and merged Nagham's `fix/mcp-auth-and-gaps` branch (already
on `main` via PR #18: Bearer token auth wired into both MCP servers, a ruff
cleanup, and `TooManyCrashesError` handling) into `yamandahle-hw6`, fixed one
leftover ruff violation, then fast-forward merged the combined branch into
`main`. No conflicts; 86 tests green before and after.

**Decision:** Switched `config.json` `llm.model` from `llama3` to `phi3:mini`.  
**Reason:** Only `phi3:mini` was actually pulled in local Ollama; smaller/
faster for iterative development, swappable via config later.

**Action:** Began Phase 3 (orchestrator). Completed, in TDD order:
1. `shared/config.py` — first-ever config-file loader in the repo (Phase 1–2
   code took values as constructor args directly; nothing read `config.json`
   until now).
2. `api_gatekeeper.py` — single choke point for LLM calls: rate limiting
   (sleeps rather than rejecting), retries, call logging, `ApiCallError`
   after retries exhausted.
3. `orchestrator/prompt_builder.py` — system + user prompt construction per
   the PRD's format, fog-of-war-aware opponent description, optional
   Q-table hint line.
4. `orchestrator/mcp_client.py` — thin async wrapper calling the cop/thief
   MCP servers as a client, attaching `authorization: Bearer <token>`.

**Bug found & fixed:** Discovered while building the MCP client that
Nagham's auth fix requires `authorization` as a **tool-call argument**, not
an HTTP header. This broke the already-pushed Phase 2 demo scripts
(`demo_mcp.py`, `scripts/call_servers.py`), which predate her fix. Fixed
both to send the argument; also fixed a pre-existing, previously-unexercised
bug in `demo_mcp.py`'s `show()` helper (assumed all results were iterable,
which only holds for `list_tools()`) and a Windows console encoding crash
from a `→`/`✓` character. Verified both scripts run cleanly end-to-end
(in-process and over real HTTP) after the fixes.

**Result:** 123 tests passing, 0 ruff violations, 97.64% coverage.

---

<!-- Add new entries below as development progresses -->
