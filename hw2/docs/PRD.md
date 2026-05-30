# PRD — AI Debate System (HW2)

## Project Overview
An automated multi-agent debate system where two AI agents argue opposing sides
of "Remote Work vs Office Work", supervised by a Father agent that enforces rules,
prevents alignment, and declares a winner based on persuasion power — not facts.

## Problem Statement
Demonstrate adversarial multi-agent orchestration: agents must maintain distinct
positions under pressure to agree, communicate only through a structured intermediary,
and cite real web sources. The system must enforce contradiction automatically.

---

## Agents and Roles

### Father Agent (Judge / Moderator)
- Routes ALL messages: Child → Father → Child. Never direct Pro↔Con.
- Detects and blocks agent alignment via mandatory intervention messages.
- Enforces word count and round count from config.
- Scores and declares ONE winner (NO TIE) on persuasion power alone.
- Does not need to know the debate topic — only the rules of the game.

### Pro Agent (Remote Work Advocate)
- Argues exclusively for remote work for the entire debate.
- Unique Skill: statistical and data-driven argument framing.
- Must cite ≥1 live web source per argument.
- Must directly reference opponent's previous argument by round number.
- System prompt blocks agreement at the instruction level.

### Con Agent (Office Work Advocate)
- Argues exclusively for office work for the entire debate.
- Unique Skill: human psychology and organizational culture framing.
- Must cite ≥1 live web source per argument.
- Must directly reference opponent's previous argument by round number.
- System prompt blocks agreement at the instruction level.

---

## Acceptance Criteria (8 Mandatory Requirements)

| # | Requirement | Definition of Done |
|---|-------------|-------------------|
| 1 | Respectful dialogue, one at a time, word-limited | Each message ≤ 150 words; Father blocks over-limit responses |
| 2 | Real contradiction via distinct Skills | Pro uses stats framing; Con uses psychology; Father detects overlap and intervenes |
| 3 | ≥ 10 pings per side | Round counter logged; debate log shows ≥ 10 exchanges per agent |
| 4 | Mutual reference | Each message quotes opponent's round number explicitly |
| 5 | Web search with real citations | Every argument includes ≥ 1 verified URL from live Tavily search |
| 6 | No tie — winner declared | Father output contains winner field + scores (e.g., 7/10 vs 5/10) |
| 7 | All comms through Father only | No direct Pro↔Con queue exists in code |
| 8 | JSON communication format | All messages validate against DebateMessage schema before sending |

---

## Non-Functional Requirements

### Performance
- API call timeout: ≤ 30 seconds (configurable in setup.json)
- Full debate (10 rounds): completes within 15 minutes
- Watchdog restart time: ≤ 5 seconds per fallen process

### Security
- Zero hardcoded secrets — all via `os.environ.get()` from `.env`
- `.env` git-ignored; `.env-example` committed with placeholder values
- No API key logged anywhere in structured logs

### Cost Control
- Gatekeeper logs input tokens, output tokens, model, and cost per call
- Rate limits enforced from `config/rate_limits.json` — never hardcoded
- FIFO queue absorbs bursts — no silent overspend
- Cost table in README populated from actual run data (not estimates)

---

## Assumptions
- Anthropic API key is available and funded for ~20 API calls per run
- Tavily API key is available for web search
- Python 3.10+ and UV package manager are installed
- Internet access is available during debate execution

## Dependencies
- `anthropic` — LLM API calls
- `tavily-python` — live web search
- `python-dotenv` — environment loading
- `pytest` + `pytest-cov` — testing and coverage
- `ruff` — linting (zero errors required)

## Limitations
- Debate topic is fixed at startup via config — not dynamically changeable mid-run
- Father judges persuasion structurally (novelty, citation quality, reference to opponent)
  not semantically — a truly brilliant argument may score the same as a structured one
- Web search depends on Tavily availability; system retries once before failing gracefully

---

## Success Metrics
- Debate completes 10 rounds without human intervention
- Father declares a non-tie winner with numerical scores and written justification
- `ruff check .` returns zero errors
- `pytest --cov` reports ≥ 85% coverage
- Actual cost per full run is documented in README cost table
- All logs structured, rotated, capped at 20 files / 500 lines per config
