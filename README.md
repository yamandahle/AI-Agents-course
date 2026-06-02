# AI Agents Course

Repository for the **AI Agents** course (Dr. Yoram Segal).

| Assignment | Folder | Description |
|------------|--------|-------------|
| HW1 | [`hw1/`](hw1/) | Signal separation with FC, RNN, and LSTM |
| HW2 | [`hw2/`](hw2/) | Multi-agent debate: PRO, CON, and Father moderator |

---

## Table of Contents

1. [Repository contents](#1-repository-contents)
2. [HW2 — stages and documentation](#2-hw2--stages-and-documentation)
3. [HW2 — quick start (Stage 3)](#3-hw2--quick-start-stage-3)
4. [HW2 — deliverables](#4-hw2--deliverables)
5. [HW1](#5-hw1)

---

## 1. Repository contents

- **HW1** — neural networks for blind source separation on mixed sine signals ([`hw1/README.md`](hw1/README.md)).
- **HW2** — three-stage implementation of an AI debate on *remote work vs. office work* ([`hw2/README.md`](hw2/README.md)).

---

## 2. HW2 — stages and documentation

HW2 is built in three ordered stages. Goals and file locations are documented in [`hw2/README.md` § Development stages](hw2/README.md#2-development-stages).

| Stage | Goal (summary) | Folder |
|-------|----------------|--------|
| 1 | Manual debate; human as Father | [`hw2/stage1/`](hw2/stage1/) |
| 2 | Semi-automatic debate via Claude CLI | [`hw2/stage2/`](hw2/stage2/), [`hw2/.claude/commands/`](hw2/.claude/commands/) |
| 3 | Full Python automation, tests, Gatekeeper | [`hw2/debate_agents/`](hw2/debate_agents/) |

---

## 3. HW2 — quick start (Stage 3)

```powershell
cd hw2/debate_agents
uv sync
copy .env-example .env
```

Configure API keys in `.env`, then:

```powershell
uv run python src/main.py
```

Technical details: [`hw2/debate_agents/README.md`](hw2/debate_agents/README.md)

---

## 4. HW2 — deliverables

| Stage | Deliverable | Path |
|-------|-------------|------|
| 1 | Debate transcript | [`hw2/stage1/debate_transcript.md`](hw2/stage1/debate_transcript.md) |
| 1 | Observations | [`hw2/stage1/observations.md`](hw2/stage1/observations.md) |
| 2 | CLI commands | [`hw2/.claude/commands/`](hw2/.claude/commands/) |
| 3 | Sample run | [`hw2/debate_agents/results/sample_debate.txt`](hw2/debate_agents/results/sample_debate.txt) |
| 3 | Test report | [`hw2/debate_agents/results/test_results.txt`](hw2/debate_agents/results/test_results.txt) |

Planning documents: [`hw2/docs/`](hw2/docs/)

---

## 5. HW1

Installation, experiments, and analysis: [`hw1/README.md`](hw1/README.md)

---

## License

Course assignments — academic use.
