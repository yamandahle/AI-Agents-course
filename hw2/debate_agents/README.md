# Debate Agents — HW2: AI Multi-Agent System

A three-agent debate system where **PRO** and **CON** agents argue "Is remote work better than office work?" while a neutral **FATHER** agent moderates, detects violations, and produces a scored verdict.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FatherAgent                        │
│  • Routes turns (PRO → CON → PRO → ...)             │
│  • Detects: agreement, repetition, contradiction     │
│  • Scores each round (ArgumentScorer)               │
│  • LLM self-evaluation (5 structured questions)     │
│  • Produces final verdict — no 50/50 ties allowed   │
└────────────┬──────────────────────┬─────────────────┘
             │                      │
    ┌────────▼────────┐    ┌────────▼────────┐
    │    ProAgent     │    │    ConAgent     │
    │  Argues FOR     │    │  Argues AGAINST │
    │  remote work    │    │  remote work    │
    │                 │    │                 │
    │ Skills:         │    │ Skills:         │
    │ • Statistical   │    │ • News Analysis │
    │   Reasoning     │    │ • Logical       │
    │ • Web Search    │    │   Fallacy Det.  │
    │   (Tavily)      │    │ • Web Search    │
    └─────────────────┘    └─────────────────┘
             │                      │
             └──────────┬───────────┘
                        │
              ┌─────────▼─────────┐
              │   ApiGatekeeper   │
              │ Rate limiting     │
              │ Retry + backoff   │
              │ Budget tracking   │
              │ Cost reporting    │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │   DebateLogger    │
              │ JSON log files    │
              │ Auto-rotation     │
              └───────────────────┘
```

---

## Scoring System

The Father uses a **two-stage scoring formula** to prevent 50/50 ties:

| Component | Weight | Method |
|-----------|--------|--------|
| Round tally | 60% | `50 + (pro_wins - con_wins) / total_rounds × 30` |
| LLM evaluation | 40% | 5 questions (novelty, evidence, rebuttal, logic, persuasion) scored 0–10 |

A minimum gap of **2 points** is enforced. If scores are equal, the side that won more rounds gets the tie-break. Scores always sum to 100.

---

## Agent Skills

| Agent | Specialist Skills |
|-------|------------------|
| PRO | Statistical Reasoning — validates data quality and highlights strong stats |
| CON | News Argumentation Analysis — dissects evidence claims; Logical Fallacy Detection — exposes reasoning errors |
| FATHER | 5-question LLM self-evaluation for final verdict |

---

## Project Structure

```
debate_agents/
├── src/
│   ├── main.py                          # Entry point
│   ├── menu.py                          # Interactive menu
│   ├── menu_handlers.py                 # Menu action handlers
│   └── debate/
│       ├── agents/
│       │   ├── base_agent.py            # Abstract base + DebateMessage
│       │   ├── agent_mixin.py           # Shared LLM/evidence helpers
│       │   ├── models.py                # DebateMessage dataclass
│       │   ├── pro_agent.py             # PRO debater
│       │   ├── con_agent.py             # CON debater
│       │   ├── father_agent.py          # Moderator + orchestrator
│       │   ├── father_checks.py         # Agreement/repetition detection
│       │   ├── father_routing.py        # Routing + intervention mixin
│       │   ├── father_scoring.py        # ArgumentScorer + DebateResult
│       │   └── father_verdict.py        # Scoring formula + LLM evaluation
│       ├── shared/
│       │   ├── gatekeeper.py            # Rate limiting + cost tracking
│       │   ├── logger.py                # JSON rotating logger
│       │   ├── watchdog.py              # Process monitor
│       │   └── config.py               # Config loader
│       └── skills/
│           ├── pro_skill.md             # PRO persona + debate rules
│           ├── con_skill.md             # CON persona + debate rules
│           ├── father_skill.md          # Father evaluation protocol
│           ├── Statistical_Reasoning.md
│           ├── News_Argumentation_Analysis.md
│           └── Logical_Fallacy_Detection.md
├── tests/
│   ├── unit/                            # 140+ unit tests
│   └── integration/                     # Full pipeline tests
├── config/
│   ├── setup.json                       # Debate config (rounds, model, etc.)
│   ├── rate_limits.json                 # API rate + budget limits
│   └── logging_config.json             # Log rotation settings
├── results/                             # Sample outputs (see below)
└── logs/                                # Auto-generated debate logs
```

---

## Setup

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
# 1. Install dependencies
uv sync

# 2. Create your .env file
cp .env.example .env
# Edit .env and add your real API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   TAVILY_API_KEY=tvly-...

# 3. Run the debate
uv run python src/main.py
```

---

## Running Tests

```bash
# Run all tests with coverage report
uv run pytest tests/

# Run only unit tests
uv run pytest tests/unit/ -q

# Run only integration tests
uv run pytest tests/integration/ -q
```

Expected output: **161 tests passed, 86% coverage** (minimum required: 85%).

---

## Running the Debate

Launch the interactive menu:

```bash
uv run python src/main.py
```

Menu options:
1. **Start Debate** — runs all 10 rounds and prints the verdict
2. **View Transcript** — shows the last debate's full argument log
3. **Cost Report** — shows API token usage and USD cost per call
4. **View Logs** — shows the last 20 log entries
5. **Exit**

---

## Configuration

Edit `config/setup.json` to change debate parameters:

```json
{
  "debate": {
    "rounds": 10,
    "word_limit": 150,
    "model": "claude-haiku-4-5",
    "timeout_seconds": 30
  }
}
```

Edit `config/rate_limits.json` to adjust API budget and rate limits.

---

## Key Design Decisions

- **No direct agent communication** — agents only exchange `DebateMessage` objects through the Father; they never hold references to each other.
- **All API calls through Gatekeeper** — no agent touches the Anthropic client directly; rate limiting, retries, and budget enforcement are centralized.
- **No 50/50 ties** — the scoring formula uses round tally as primary signal and LLM evaluation as secondary; a minimum 2-point gap is always enforced.
- **All config from files** — zero hardcoded values in code; everything lives in `config/`.
- **No API keys in code** — loaded exclusively from `.env` via `python-dotenv`.

---

## Results

See the `results/` folder for:
- `sample_debate.txt` — full output from a real 10-round debate
- `test_results.txt` — pytest coverage report
