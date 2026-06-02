# Debate Agents — Stage 3 (Python)

**Assignment:** HW2 — AI Agents  
**Topic:** Is remote work better than working from the office?

This folder contains **Stage 3** of the project: a fully automated three-agent debate system (PRO, CON, Father).

**Stage goals and Stages 1–2:** see [`../README.md`](../README.md#2-development-stages).

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Architecture](#2-architecture)
3. [Installation](#3-installation)
4. [Running the application](#4-running-the-application)
5. [Configuration](#5-configuration)
6. [Testing and quality](#6-testing-and-quality)
7. [Cost analysis](#7-cost-analysis)
8. [Project layout](#8-project-layout)
9. [Results](#9-results)
10. [Related documentation](#10-related-documentation)

---

## 1. Purpose

| Component | Responsibility |
|-----------|----------------|
| **ProAgent** | Argues that remote work is superior; uses statistical reasoning and web search |
| **ConAgent** | Argues that office work is superior; uses evidence analysis and fallacy detection |
| **FatherAgent** | Routes turns, checks agreement/repetition/contradiction, scores rounds, declares winner |
| **ApiGatekeeper** | All Anthropic API calls; rate limits, retries, per-call cost logging |
| **DebateSDK** | Public entry point for starting and executing debates |
| **DebateOrchestrator** | Runs debate in a subprocess with Watchdog and event streaming |

---

## 2. Architecture

```
Terminal menu (main.py)
        │
        ▼
   DebateSDK (sdk.py)
        │
        ▼
 DebateOrchestrator  ──►  Watchdog + multiprocessing
        │
        ▼
 FatherAgent ──► ProAgent / ConAgent
        │
        ▼
 ApiGatekeeper ──► Anthropic API
 DebateLogger  ──► JSON log files (rotating)
```

**Scoring:** 60% round wins + 40% LLM evaluation (five criteria). Minimum score gap: 2 points. Total always sums to 100.

---

## 3. Installation

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```powershell
uv sync
copy .env-example .env
```

Environment variables (see `.env-example`):

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | LLM API |
| `TAVILY_API_KEY` | Web search for citations |

The file `.env` is listed in `.gitignore` and must not be committed.

---

## 4. Running the application

```powershell
uv run python src/main.py
```

| Option | Description |
|--------|-------------|
| 1 | Execute full debate (default: 10 rounds); writes `results/sample_debate.txt` |
| 2 | Show transcript and verdict from last run |
| 3 | Show Gatekeeper cost table |
| 4 | Show last 20 structured log entries |
| 5 | Exit |

---

## 5. Configuration

Parameters are loaded from `config/` (no hardcoded values in application code).

**`config/setup.json`**

| Key | Default | Description |
|-----|---------|-------------|
| `debate.rounds` | 10 | Number of debate rounds |
| `debate.word_limit` | 150 | Maximum words per argument |
| `debate.model` | claude-haiku-4-5 | Anthropic model id |

**`config/rate_limits.json`** — requests per minute, daily budget, model pricing.

**`config/logging_config.json`** — log directory, max files, max lines per file.

---

## 6. Testing and quality

```powershell
uv run ruff check .
uv run pytest tests/
```

| Metric | Value |
|--------|-------|
| Tests | 161 passed |
| Coverage | ~86% (minimum required: 85%) |
| Report | [`results/test_results.txt`](results/test_results.txt) |

---

## 7. Cost analysis

Measured from one complete 10-round run (`logs/debate_20260602_180328_337838_0001.log`):

| Model | API calls | Input tokens | Output tokens | Total (USD) |
|-------|-----------|--------------|---------------|-------------|
| claude-haiku-4-5 | 53 | ~118,500 | ~33,800 | 0.254 |

Pricing is defined in `config/rate_limits.json`. The Gatekeeper enforces rate limits and a daily budget cap (`daily_budget_usd`).

---

## 8. Project layout

```
debate_agents/
  src/           Application code (agents, SDK, menu)
  tests/         Unit and integration tests
  config/        setup.json, rate_limits.json, logging_config.json
  docs/          PRD, PLAN, TODO (copy; see also ../docs/)
  results/       sample_debate.txt, test_results.txt
  logs/          Runtime logs (git-ignored)
```

---

## 9. Results

| File | Contents |
|------|----------|
| [`results/sample_debate.txt`](results/sample_debate.txt) | Full transcript, final verdict, cost summary |
| [`results/test_results.txt`](results/test_results.txt) | Pytest output and coverage |

---

## 10. Related documentation

| Document | Path |
|----------|------|
| HW2 overview and all stages | [`../README.md`](../README.md) |
| Product requirements | [`../docs/PRD.md`](../docs/PRD.md) |
| Architecture plan | [`../docs/PLAN.md`](../docs/PLAN.md) |
| Task tracker | [`docs/TODO.md`](docs/TODO.md) |

---

## License

Course assignment — academic use.
