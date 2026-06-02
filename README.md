# AI Agents Course

Student repository for the **AI Agents** course (Dr. Yoram Segal).

| Assignment | Folder | What it does |
|------------|--------|----------------|
| HW1 | [`hw1/`](hw1/) | Signal separation with FC, RNN, and LSTM |
| HW2 | [`hw2/`](hw2/) | Multi-agent debate: PRO vs CON, moderated by Father |

---

## Table of Contents

1. [Repository overview](#1-repository-overview)
2. [HW2 — quick start](#2-hw2--quick-start)
3. [HW2 — evidence and results](#3-hw2--evidence-and-results)
4. [Documentation](#4-documentation)
5. [HW1](#5-hw1)

---

## 1. Repository overview

This repo contains two assignments:

- **HW1** — machine learning on noisy mixed signals (fully documented in [`hw1/README.md`](hw1/README.md)).
- **HW2** — three-stage debate system on the topic *“Is remote work better than working from the office?”*
  - **PRO** argues for remote work
  - **CON** argues for office work
  - **Father** routes all messages, enforces rules, and declares a winner (no ties)

HW2 is submitted on branch **`yamandahle-hw2`** (see [GitHub](https://github.com/yamandahle/AI-Agents-course)).

---

## 2. HW2 — quick start

The runnable Python app lives in **`hw2/debate_agents/`**.

```powershell
cd hw2/debate_agents
uv sync
copy .env-example .env
# Edit .env: set ANTHROPIC_API_KEY and TAVILY_API_KEY
uv run python src/main.py
```

**Menu:** `1` = run debate · `2` = transcript · `3` = cost report · `4` = logs · `5` = exit

After option **1**, the full run is saved to [`hw2/debate_agents/results/sample_debate.txt`](hw2/debate_agents/results/sample_debate.txt).

Full guide: [`hw2/README.md`](hw2/README.md) · Technical details: [`hw2/debate_agents/README.md`](hw2/debate_agents/README.md)

---

## 3. HW2 — evidence and results

Chat screenshots are **not required** — transcripts and logs are in the repo:

| What | File |
|------|------|
| Stage 1 manual debate (ChatGPT + Gemini) | [`hw2/stage1/debate_transcript.md`](hw2/stage1/debate_transcript.md) |
| Stage 1 lessons learned | [`hw2/stage1/observations.md`](hw2/stage1/observations.md) |
| Stage 2 Claude CLI prompts | [`hw2/.claude/commands/`](hw2/.claude/commands/) |
| Stage 3 sample run (transcript + verdict + cost) | [`hw2/debate_agents/results/sample_debate.txt`](hw2/debate_agents/results/sample_debate.txt) |
| Stage 3 tests (161 passed, ~86% coverage) | [`hw2/debate_agents/results/test_results.txt`](hw2/debate_agents/results/test_results.txt) |

---

## 4. Documentation

| Document | Location |
|----------|----------|
| HW2 overview (3 stages) | [`hw2/README.md`](hw2/README.md) |
| Product requirements | [`hw2/docs/PRD.md`](hw2/docs/PRD.md) |
| Architecture plan | [`hw2/docs/PLAN.md`](hw2/docs/PLAN.md) |
| Task tracker | [`hw2/docs/TODO.md`](hw2/docs/TODO.md) |

---

## 5. HW1

Installation, experiments, figures, and analysis: [`hw1/README.md`](hw1/README.md)

---

## License

Course assignments — academic use.
