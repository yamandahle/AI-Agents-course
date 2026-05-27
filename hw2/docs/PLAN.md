# 🗺️ System Engineering Plan & Developer Guide

Welcome to the Exercise 02 Multi-Agent Debate Platform. This document outlines the system architecture, process workflows, and code guidelines required to maintain development alignment.

---

## 🏗️ 1. Software Architecture & OOP Hierarchy
To comply with strict software standards and eliminate code duplication, our system utilizes robust Object-Oriented Programming (OOP) inheritance.
### Class Design Blueprint
* **`BaseAgent` (`src/sdk/models/base_agent.py`)**: Abstract parent class. Handles loading project-scoped markdown personas from disk, instantiating the correct runtime client factory, tracking token usage, and interfacing with the rotating FIFO logger.
* **`JudgeAgent` (`src/sdk/models/judge_agent.py`)**: Subclass extending `BaseAgent`. Implements specialized arbitration logic, manages the cumulative text log, and enforces the strict binary evaluation protocol (no-tie condition).
* **`DebaterAgent` (`src/sdk/models/debater_agent.py`)**: Subclass extending `BaseAgent`. Implements stance-specific persona execution and invokes the external search tool to embed internet grounding citations.

---

## 🔄 2. Multi-Process Orchestration & IPC Flow
Every agent runs as an entirely independent operating system process to guarantee true isolation. Communication never occurs directly between debaters; everything passes strictly through a secure Judge relay queue using structured JSON communication strings.
### Execution Lane Requirements
1. **The Sequence**: Main Process ──> Spawn Judge, Proponent, Opponent as separate tasks.
2. **Turn Limits**: The system tracks and enforces a minimum benchmark of 10 continuous ping-pong interactions per side.
3. **Session State on Disk**: After every completed turn, the system writes a formatted entry to `outputs/logs/debate_summary.md` for human auditing, and saves a line entry to `outputs/logs/session_history.jsonl` for programmatic context engineering recovery.

---

## 🛡️ 3. Safety Guardrails & Operational Constraints
* **The Background Watchdog**: A dedicated background supervisor thread monitors execution latencies. If an agent call freezes or exceeds the threshold specified in `config/setup.json`, the watchdog issues an active `os.kill` signal to clear memory and re-instantiates that worker process.
* **FIFO Log Rotations**: To protect machine disk storage, logs are routed using a First-In, First-Out layout. It automatically splits data across files capped at 500 lines each.
* **No Hardcoded Parameters**: Absolutely every operational asset—from timeout boundaries to token caps and the debate topic—must be loaded directly from `config/setup.json`.

---

## 🛠️ 4. Onboarding Checklist for Partners
When developing on your local machine, maintain these project settings:

1. **Local Setup**: Run `uv sync` to install all dependencies inside an isolated virtual workspace.
2. **Secrets Security**: Create your own localized `.env` file at the project root. Paste your secret key as `ACTIVE_API_KEY=your_key`. Never push this file to Git!
3. **Toggle Providers**: To switch between models, open `config/setup.json` and modify the `"use_provider"` field. The Python backend factory handles the conversion seamlessly.
4. **Code Quality Gates**: Before creating a Pull Request, verify your scripts match style parameters by executing:
   ```bash
   uv run ruff check src/
   uv run pytest
