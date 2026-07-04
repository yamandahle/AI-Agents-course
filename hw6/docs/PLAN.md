# PLAN — Cop & Thief: Dual AI Agents via MCP (EX06)

**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft — awaiting review

---

## 1. Resolved Design Decisions

These were open questions in PRD.md — resolved here before coding starts.

| Question | Decision | Reason |
|----------|----------|--------|
| LLM model | `llama3` via Ollama | Good speed/quality balance locally; swap via config |
| Q-table state | `(cop_row, cop_col, thief_row, thief_col)` only — no barriers | Keeps state space at 625; barriers change per sub-game making Q-table unstable if included |
| GUI framework | `tkinter` | Zero extra dependency; stdlib only |
| Screenshot capture | `PIL.ImageGrab` (Pillow) | Simple, cross-platform, one import |
| Deceptive thief prompts | System prompt instructs LLM to describe a false direction without using coordinates | Keeps NL-only rule; no hardcoded lies |
| Package name | `cop_thief` | Short, clear, matches assignment |
| Config format | `config.json` | Assignment specifies JSON |

---

## 2. Implementation Phases

Phases follow the assignment's recommended priority order (Section 13 of spec).
Each phase must pass its tests before the next phase begins.

---

### Phase 1 — Game Engine (SDK Core)

**Goal:** A fully working game engine with no LLM, no MCP, no GUI.

**Files to create:**
```
src/cop_thief/sdk/game_engine/board.py
src/cop_thief/sdk/game_engine/observation.py
src/cop_thief/sdk/game_engine/sub_game.py
src/cop_thief/sdk/game_engine/game_session.py
src/cop_thief/sdk/__init__.py
src/cop_thief/sdk/game_engine/__init__.py
config/config.json
src/cop_thief/version.py
tests/unit/test_board.py
tests/unit/test_observation.py
tests/unit/test_sub_game.py
tests/integration/test_game_session.py
```

**Done when:**
- All 10 game engine tests pass
- A 2×1 grid sub-game runs to completion in pure Python (no LLM)
- Coverage ≥ 85% on game_engine/

---

### Phase 2 — MCP Servers

**Goal:** Two FastMCP servers running locally on separate ports, exposing tools.

**Files to create:**
```
src/cop_thief/mcp/cop_server.py
src/cop_thief/mcp/thief_server.py
src/cop_thief/mcp/tools.py
src/cop_thief/mcp/__init__.py
tests/unit/test_mcp_tools.py
tests/integration/test_mcp_servers.py
.env.example
```

**Done when:**
- Both servers start on ports 8001 and 8002
- `get_observation`, `send_message`, `make_move`, `place_barrier` all respond correctly
- Auth token rejects unauthorized requests (401)
- All MCP tests pass with mocked game engine

---

### Phase 3 — Full Local Run (Orchestrator + LLM)

**Goal:** Both agents play a complete 6-sub-game session autonomously via LLM.

**Files to create:**
```
src/cop_thief/orchestrator/game_loop.py
src/cop_thief/orchestrator/prompt_builder.py
src/cop_thief/orchestrator/action_parser.py
src/cop_thief/orchestrator/mcp_client.py
src/cop_thief/orchestrator/__init__.py
src/cop_thief/api_gatekeeper.py
config/rate_limits.json
src/main.py
tests/unit/test_prompt_builder.py
tests/unit/test_action_parser.py
tests/integration/test_game_loop.py
```

**Done when:**
- `uv run python src/main.py` runs a full game (headless) with Ollama running locally
- LLM controls both agents; messages exchanged each turn in natural language
- Game completes 6 sub-games and prints final scores
- All retries and fallbacks work correctly
- Sanity check: 3×2 grid completes without crash

---

### Phase 4 — Q-Table Advisor

**Goal:** Train a Q-table via self-play; inject its hint into LLM prompt.

**Files to create:**
```
src/cop_thief/sdk/q_table/advisor.py
src/cop_thief/sdk/q_table/trainer.py
src/cop_thief/sdk/q_table/__init__.py
tests/unit/test_q_table_advisor.py
tests/unit/test_q_table_trainer.py
```

**Done when:**
- `uv run python -m cop_thief.sdk.q_table.trainer` trains and saves `config/q_table.npy`
- Q-table hint appears in LLM prompt when `q_table.enabled = true`
- With `q_table.enabled = false`, no hint, behavior identical to Phase 3
- Cop win rate with Q-table ≥ cop win rate without (measured over 3 games)

---

### Phase 5 — GUI

**Goal:** Visual board that updates in real time during a game.

**Files to create:**
```
src/cop_thief/gui/board_view.py
src/cop_thief/gui/info_panel.py
src/cop_thief/gui/screenshot.py
src/cop_thief/gui/app.py
src/cop_thief/gui/__init__.py
tests/unit/test_gui_screenshot.py
```

**Done when:**
- `uv run python src/main.py` with `gui.enabled = true` shows live board
- Screenshots save to `assets/screenshots/` at all 5 trigger points
- Headless mode (`gui.enabled = false`) runs identically with no window
- Sanity check: 5×5 grid renders correctly with barriers and agent icons

---

### Phase 6 — Gmail Report

**Goal:** Cop agent emails JSON report after game ends.

**Files to create:**
```
src/cop_thief/gmail/report_builder.py
src/cop_thief/gmail/auth.py
src/cop_thief/gmail/sender.py
src/cop_thief/gmail/__init__.py
tests/unit/test_report_builder.py
tests/unit/test_gmail_sender.py
```

**Done when:**
- After 6 sub-games, one email sent automatically to lecturer address
- Email body is valid JSON only (no free text)
- All Gmail tests pass with mocked API
- Manual verification: email received at `rmisegal+uoh26b@gmail.com`

---

### Phase 7 — Experiments

**Goal:** Run all 7 cases, collect results, generate graphs, write notebook.

**Files to create:**
```
src/cop_thief/experiments/runner.py
src/cop_thief/experiments/cases.py
src/cop_thief/experiments/metrics.py
src/cop_thief/experiments/graphs.py
src/cop_thief/experiments/__init__.py
notebooks/experiments.ipynb
tests/unit/test_experiment_cases.py
tests/integration/test_experiment_runner.py
```

**Done when:**
- `uv run python -m cop_thief.experiments.runner --all` completes all 7 cases
- `results/summary.csv` has 7 rows with all metrics
- All 5 graphs saved to `results/graphs/`
- Screenshots exist for all cases in `assets/screenshots/`
- Notebook runs end-to-end with analysis written

---

## 3. Dependency Graph

```
Phase 1 (Game Engine)
    └── Phase 2 (MCP Servers)
            └── Phase 3 (Orchestrator + LLM)
                    ├── Phase 4 (Q-Table)      ← parallel with Phase 5
                    ├── Phase 5 (GUI)           ← parallel with Phase 4
                    └── Phase 6 (Gmail)
                            └── Phase 7 (Experiments)
```

Phases 4 and 5 can be developed in parallel by two team members.

---

## 4. Project Setup

### First-time setup
```bash
# Install uv if not already installed
pip install uv

# Clone and enter repo
git clone https://github.com/yamandahle/AI-Agents-course.git
cd AI-Agents-course
git checkout yamandahle-hw6
cd hw6

# Install dependencies
uv sync

# Copy env file and fill in values
cp .env.example .env

# Install and start Ollama
ollama pull llama3
ollama serve
```

### Daily workflow
```bash
uv run pytest tests/ --cov                  # run all tests with coverage
uv run ruff check .                          # lint check
uv run python src/main.py                    # run full game (headless)
uv run python src/main.py --gui              # run with visual board
uv run python -m cop_thief.sdk.q_table.trainer   # train Q-table
uv run python -m cop_thief.experiments.runner --all  # run all experiments
```

---

## 5. pyproject.toml Structure

```toml
[project]
name = "cop-thief"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=0.1",
    "httpx>=0.27",
    "pillow>=10.0",
    "google-api-python-client>=2.0",
    "google-auth-oauthlib>=1.0",
    "google-auth-httplib2>=0.2",
    "numpy>=1.26",
    "matplotlib>=3.8",
    "seaborn>=0.13",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "jupyter>=1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.coverage.report]
fail_under = 85

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I"]
```

---

## 6. Team Split (Suggested)

| Member | Phases | Files |
|--------|--------|-------|
| Member 1 | 1, 2, 3, 6 | Game engine, MCP servers, orchestrator, Gmail |
| Member 2 | 4, 5, 7 | Q-table, GUI, experiments, notebook |

Both members: write tests for their own phases before implementation (TDD).

---

## 7. Definition of Done (Full Project)

- [ ] `uv run pytest tests/ --cov` → coverage ≥ 85%, all tests green
- [ ] `uv run ruff check .` → 0 violations
- [ ] Full game runs headlessly end-to-end with Ollama
- [ ] GUI shows live board with screenshots saved
- [ ] Gmail report received by lecturer after game
- [ ] All 7 experiment cases complete with graphs and notebook
- [ ] All docs committed: PRD.md, PLAN.md, TODO.md, 6 mechanism PRDs, PROMPTS.md
- [ ] No hardcoded parameters anywhere in code
- [ ] No secrets committed (`.env` git-ignored)
- [ ] `version.py` starts at `1.00`
- [ ] Every function, class, and module has a docstring
- [ ] Each `.py` file ≤ 150 code lines
