# HW2 — AI Debate System

**Course:** AI Agents  
**Topic:** Is remote work better than working from the office?

Two debater agents (**PRO**, **CON**) argue opposing positions. A third agent (**Father**) moderates, enforces rules, and declares a winner. All messages pass through Father only (no direct PRO ↔ CON).

---

## Table of Contents

1. [Project overview](#1-project-overview)
2. [Development stages](#2-development-stages)
3. [Installation and execution](#3-installation-and-execution)
4. [Evidence and deliverables](#4-evidence-and-deliverables)
5. [Repository layout](#5-repository-layout)
6. [Planning documentation](#6-planning-documentation)
7. [Design decisions](#7-design-decisions)

---

## 1. Project overview

| Agent | Position |
|-------|----------|
| **PRO** | Remote work is better than office work |
| **CON** | Office work is better than remote work |
| **Father** | Routes turns, detects rule violations, scores arguments, produces final verdict (no 50/50 tie) |

The assignment is implemented in **three stages**, from fully manual operation to full Python automation.

---

## 2. Development stages

Stages are listed in the order they were built. Each stage has a defined goal and concrete outputs.

### Stage 1 — Manual debate

| | |
|---|---|
| **Goal** | Learn how two LLMs behave in adversarial debate when a human acts as moderator; observe agreement, repetition, and citation quality without code. |
| **Method** | PRO runs in ChatGPT; CON runs in Gemini. The human copies arguments between tools and plays the role of Father (turn order and final judgment). |
| **Rounds** | 5 |
| **Outputs** | Prompts, full transcript, written observations |
| **Location** | [`stage1/`](stage1/) |

| File | Description |
|------|-------------|
| [`stage1/pro_prompt.md`](stage1/pro_prompt.md) | System prompt for PRO (ChatGPT) |
| [`stage1/con_prompt.md`](stage1/con_prompt.md) | System prompt for CON (Gemini) |
| [`stage1/HOW_TO_RUN.md`](stage1/HOW_TO_RUN.md) | Step-by-step procedure |
| [`stage1/debate_transcript.md`](stage1/debate_transcript.md) | Recorded debate |
| [`stage1/observations.md`](stage1/observations.md) | Findings and lessons |

---

### Stage 2 — Semi-automatic debate (Claude CLI)

| | |
|---|---|
| **Goal** | Run PRO, CON, and Father in one session using saved commands; enforce JSON messages, web citations, and Father interventions without custom Python. |
| **Method** | Claude CLI loads skill files from [`.claude/commands/`](.claude/commands/). The command `/start_debate` runs the full debate flow. |
| **Rounds** | 5 (configurable in command files) |
| **Outputs** | Command definitions (`pro_skill`, `con_skill`, `father_skill`, `start_debate`), run instructions |
| **Location** | [`stage2/`](stage2/), [`.claude/commands/`](.claude/commands/) |

| File | Description |
|------|-------------|
| [`stage2/HOW_TO_RUN.md`](stage2/HOW_TO_RUN.md) | How to start Claude CLI and run `/start_debate` |
| [`.claude/commands/pro_skill.md`](.claude/commands/pro_skill.md) | PRO agent behavior |
| [`.claude/commands/con_skill.md`](.claude/commands/con_skill.md) | CON agent behavior |
| [`.claude/commands/father_skill.md`](.claude/commands/father_skill.md) | Father moderation and scoring |
| [`.claude/commands/start_debate.md`](.claude/commands/start_debate.md) | Main debate orchestration command |

---

### Stage 3 — Full automation (Python)

| | |
|---|---|
| **Goal** | Implement the full debate as a maintainable software system: OOP agents, API Gatekeeper, structured logging, SDK entry point, multiprocessing orchestrator, Watchdog, terminal menu, and automated tests (≥ 85% coverage). |
| **Method** | Python 3.11+ project managed with `uv`. External calls go through `ApiGatekeeper`. Business logic is exposed via `DebateSDK`. The CLI menu only displays events and reads configuration. |
| **Rounds** | 10 (configured in `debate_agents/config/setup.json`) |
| **Outputs** | Source code, tests, sample run log, cost report |
| **Location** | [`debate_agents/`](debate_agents/) |

| File | Description |
|------|-------------|
| [`debate_agents/README.md`](debate_agents/README.md) | Stage 3 technical documentation |
| [`debate_agents/results/sample_debate.txt`](debate_agents/results/sample_debate.txt) | Transcript, verdict, and cost summary |
| [`debate_agents/results/test_results.txt`](debate_agents/results/test_results.txt) | Pytest and coverage report |

**Representative verdict (10-round run):** PRO 53% — CON 47% (round wins: PRO 6, CON 4).

---

## 3. Installation and execution

### Stage 3 (primary runnable system)

```powershell
cd debate_agents
uv sync
copy .env-example .env
```

Set `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` in `.env` (see `.env-example`). Then:

```powershell
uv run python src/main.py
```

| Menu option | Function |
|-------------|----------|
| 1 | Run 10-round debate; saves `results/sample_debate.txt` |
| 2 | Display last transcript and verdict |
| 3 | Display API cost report |
| 4 | Display recent structured logs |
| 5 | Exit |

**Quality checks:**

```powershell
uv run ruff check .
uv run pytest tests/
```

### Stage 2

```powershell
cd hw2
claude
```

In the CLI session: `/start_debate`

### Stage 1

Follow [`stage1/HOW_TO_RUN.md`](stage1/HOW_TO_RUN.md).

---

## 4. Evidence and deliverables

| Stage | Deliverable | Path |
|-------|-------------|------|
| 1 | Debate transcript | [`stage1/debate_transcript.md`](stage1/debate_transcript.md) |
| 1 | Observations | [`stage1/observations.md`](stage1/observations.md) |
| 2 | CLI commands | [`.claude/commands/`](.claude/commands/) |
| 3 | Sample debate output | [`debate_agents/results/sample_debate.txt`](debate_agents/results/sample_debate.txt) |
| 3 | Test report | [`debate_agents/results/test_results.txt`](debate_agents/results/test_results.txt) |

---

## 5. Repository layout

```
hw2/
  stage1/              Stage 1 — manual debate
  stage2/              Stage 2 — CLI instructions
  .claude/commands/    Stage 2 — Claude CLI skills and start_debate
  debate_agents/       Stage 3 — Python application
  docs/                PRD, PLAN, TODO, component specifications
```

---

## 6. Planning documentation

| Document | Purpose |
|----------|---------|
| [`docs/PRD.md`](docs/PRD.md) | Requirements and acceptance criteria |
| [`docs/PLAN.md`](docs/PLAN.md) | Architecture, IPC, message schema |
| [`docs/TODO.md`](docs/TODO.md) | Task tracking |
| [`docs/PRD_father_agent.md`](docs/PRD_father_agent.md) | Father agent specification |
| [`docs/PRD_debate_agents.md`](docs/PRD_debate_agents.md) | PRO and CON specification |
| [`docs/PRD_gatekeeper.md`](docs/PRD_gatekeeper.md) | API Gatekeeper specification |
| [`docs/PRD_logger_watchdog.md`](docs/PRD_logger_watchdog.md) | Logger and Watchdog specification |

---

## 7. Design decisions

| Decision | Rationale |
|----------|-----------|
| All messages through Father | Enforces assignment rule; prevents direct PRO ↔ CON communication |
| Tavily web search | Supplies real URLs for citations |
| API Gatekeeper | Centralizes rate limits, retries, token and cost logging |
| No 50/50 verdict | Father must declare a winner based on persuasion |
| DebateSDK as entry point | Separates business logic from terminal UI |
