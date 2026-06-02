# HW2 — AI Debate System

**Course:** AI Agents  
**Topic:** Is remote work better than working from the office?

Three agents debate: **PRO** (remote work), **CON** (office work), **Father** (moderator and judge).

---

## Table of Contents

1. [What this project does](#1-what-this-project-does)
2. [How to run](#2-how-to-run)
3. [Evidence and results](#3-evidence-and-results)
4. [Three stages](#4-three-stages)
5. [Project structure](#5-project-structure)
6. [Documentation](#6-documentation)
7. [Design decisions](#7-design-decisions)

---

## 1. What this project does

| Agent | Role |
|-------|------|
| **PRO** | Argues remote work is better |
| **CON** | Argues office work is better |
| **Father** | Routes every message, checks rules, scores rounds, declares one winner (no 50/50 tie) |

All communication goes **through Father only** (no direct PRO ↔ CON).

The work is built in **three stages** (manual → Claude CLI → Python).

---

## 2. How to run

### Stage 3 — Python (main submission)

```powershell
cd debate_agents
uv sync
copy .env-example .env
# Add ANTHROPIC_API_KEY and TAVILY_API_KEY to .env
uv run python src/main.py
```

| Menu | Action |
|------|--------|
| 1 | Run full 10-round debate (saves `results/sample_debate.txt`) |
| 2 | View last transcript + verdict |
| 3 | View API cost report |
| 4 | View recent logs |
| 5 | Exit |

**Tests:**

```powershell
uv run ruff check .
uv run pytest tests/
```

Expected: zero ruff errors; ≥ 85% coverage (see `debate_agents/results/test_results.txt`).

More detail: [`debate_agents/README.md`](debate_agents/README.md)

### Stage 2 — Claude CLI

```powershell
cd hw2
claude
# Then type:
/start_debate
```

Prompts: [`.claude/commands/`](.claude/commands/) · Steps: [`stage2/HOW_TO_RUN.md`](stage2/HOW_TO_RUN.md)

### Stage 1 — Manual (ChatGPT + Gemini)

1. Paste [`stage1/pro_prompt.md`](stage1/pro_prompt.md) into ChatGPT  
2. Paste [`stage1/con_prompt.md`](stage1/con_prompt.md) into Gemini  
3. Follow [`stage1/HOW_TO_RUN.md`](stage1/HOW_TO_RUN.md)

---

## 3. Evidence and results

Screenshots are optional. These files are the main proof of work:

| Stage | Evidence |
|-------|----------|
| 1 | [`stage1/debate_transcript.md`](stage1/debate_transcript.md) — full 5-round debate |
| 1 | [`stage1/observations.md`](stage1/observations.md) — what we learned |
| 2 | [`.claude/commands/`](.claude/commands/) — PRO, CON, Father, start_debate |
| 3 | [`debate_agents/results/sample_debate.txt`](debate_agents/results/sample_debate.txt) — transcript + verdict + cost |
| 3 | [`debate_agents/results/test_results.txt`](debate_agents/results/test_results.txt) — pytest report |

**Example final verdict (live run):** PRO won **53% vs 47%** after 10 rounds (round wins PRO 6 – CON 4).

---

## 4. Three stages

| Stage | Method | Automation |
|-------|--------|--------------|
| 1 | Two browser tabs + human as Father | Manual |
| 2 | Claude CLI `/start_debate` | Semi-automatic |
| 3 | Python + SDK + Gatekeeper + Watchdog | Fully automatic |

---

## 5. Project structure

```
hw2/
  stage1/           Manual debate (prompts, transcript, observations)
  stage2/           Claude CLI instructions
  .claude/commands/ Stage 2 agent skills and start_debate
  debate_agents/    Stage 3 Python project (src, tests, config)
  docs/             PRD, PLAN, TODO, component PRDs
```

---

## 6. Documentation

| File | Purpose |
|------|---------|
| [`docs/PRD.md`](docs/PRD.md) | Requirements and acceptance criteria |
| [`docs/PLAN.md`](docs/PLAN.md) | Architecture and IPC |
| [`docs/TODO.md`](docs/TODO.md) | Task status |
| [`docs/PRD_father_agent.md`](docs/PRD_father_agent.md) | Father agent spec |
| [`docs/PRD_debate_agents.md`](docs/PRD_debate_agents.md) | PRO / CON spec |
| [`docs/PRD_gatekeeper.md`](docs/PRD_gatekeeper.md) | API gatekeeper spec |
| [`docs/PRD_logger_watchdog.md`](docs/PRD_logger_watchdog.md) | Logger and watchdog spec |

---

## 7. Design decisions

| Decision | Why |
|----------|-----|
| All messages through Father | Enforces debate rules; no direct agent chat |
| Web search (Tavily) | Real citations, not invented URLs |
| API Gatekeeper | Rate limits, cost tracking, retries |
| No 50/50 ties | Father always picks a winner on persuasion |
| SDK entry point | CLI uses `DebateSDK` only — no business logic in menu |
