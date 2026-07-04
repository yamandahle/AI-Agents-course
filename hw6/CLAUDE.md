# CLAUDE.md — Project Rules (Cop & Thief: Dual AI Agents via MCP)

## What this project is
University AI Agents course assignment (EX06). Two autonomous AI agents
(Cop, Thief) play a pursuit game on a 2D grid. Each agent has its own MCP
server (FastMCP). Agents communicate ONLY in free natural language — never
raw coordinates over a rigid protocol. The LLM lives in the orchestrator
CLIENT, not inside the MCP servers. The servers only expose tools.

Full assignment spec: docs/course/ex06-assignment.pdf
Gmail OAuth guide:    docs/course/google-api-guide.pdf
Submission standards: docs/course/software-guidelines.pdf
READ ALL THREE before proposing any plan or writing any code.

## Workflow rules (strict)
- Docs BEFORE code. Order: docs/PRD.md -> docs/PLAN.md -> docs/TODO.md ->
  per-mechanism PRDs (docs/PRD_<mechanism>.md) -> only then implementation.
- Every major mechanism needs its own short PRD file BEFORE coding it:
  PRD_game_engine.md, PRD_mcp_communication.md, PRD_llm_orchestrator.md,
  PRD_gui.md, PRD_gmail_report.md, PRD_experiments.md.
- Work step by step. After each step, STOP and ask for confirmation before
  continuing. Never implement multiple stages in one shot.
- Explain decisions in simple, human language before implementing them.
- Prefer reusing existing code in the repo over writing new code.
- Do not add complexity beyond what the assignment requires.
- Update docs/TODO.md status as tasks complete.
- Append every significant prompt/decision to docs/PROMPTS.md (prompt log
  is a graded requirement).

## Code standards (from course submission guidelines — graded)
- Package manager: uv ONLY. Never pip, never `python -m`. Run everything
  via `uv run ...`. Keep pyproject.toml + uv.lock committed.
- Max 150 code lines per file (comments/blank lines excluded). Split
  files that exceed it.
- Zero `ruff check` violations. Ruff config lives in pyproject.toml.
- TDD: write the test first (red), implement (green), refactor. Coverage
  >= 85% with fail_under = 85 in pyproject.toml. Mock external services
  (LLM APIs, Gmail) in tests — tests must not call real external services.
- NO hardcoded game parameters. Everything comes from config/config.json:
  grid_size, max_moves, num_games, max_barriers, scoring, vision radii,
  LLM settings, MCP ports/URLs.
- NO secrets in code. Use .env (git-ignored) + .env-example (committed
  with dummy values). credentials.json / token.json / *.key in .gitignore.
- Architecture: all business logic behind an SDK layer
  (src/<package>/sdk/). GUI and CLI call the SDK only — zero game logic
  in GUI/CLI code.
- All external API calls (LLM, Gmail) go through a central ApiGatekeeper
  (rate limits from config/rate_limits.json, queue instead of reject,
  retries, call logging).
- OOP, no code duplication (DRY): shared logic -> base class / mixin /
  shared module.
- Every function, class, module: docstring. Comments explain WHY not what.
- Version tracking: version.py starting at 1.00; "version" key in every
  JSON config.

## Game rules (summary — full details in assignment PDF)
- Grid default 5x5, size from config (dynamic, generic architecture).
- Sub-game: max 25 moves. Full game = 6 valid sub-games (crashed ones are
  rerun). Turn-based: thief moves first, then cop.
- Moves: 8 directions (including diagonals), one cell per move.
- Cop may, instead of moving, place a barrier on its CURRENT cell (max 5
  per sub-game). Barrier cells become permanently impassable for both.
- Cop wins sub-game: lands exactly on thief's cell. Thief wins: survives
  25 moves. Scoring per sub-game: cop win -> cop 20 / thief 5;
  thief win -> thief 10 / cop 5.
- Partial observability ("fog of war"): each agent always truthfully
  knows its own position, all barriers, and the move counter. It sees the
  opponent's position ONLY within a vision radius R (Chebyshev distance,
  per-agent, from config). Natural-language messages are unconstrained:
  truth, vagueness, or deception are all allowed.
- After 6 sub-games, the COP agent automatically emails a JSON-only
  report (no free text in body) to the lecturer's address defined in
  config, via Gmail API with OAuth token (see google-api-guide.pdf).

## Testing / running quick reference
- uv sync
- uv run pytest tests/ --cov
- uv run ruff check .
- uv run python src/main.py  (or the entry point defined later)
