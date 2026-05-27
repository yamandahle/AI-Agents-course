# AI Agent Debate System - Progress Documentation

This document summarizes the development and architecture of the AI Agent Debate system implemented during this session.

## 1. Project Overview
The project is a modular Python-based multi-process architecture designed to facilitate structured, persona-driven debates between AI agents. It uses a `Judge -> Agent 1 -> Judge -> Agent 2` sequential communication flow managed by a central orchestrator.

## 2. Architectural Components

### Core Orchestration
- **`AgentBase`**: An abstract base class defining shared identity fields (`name`, `role`, `expertise`, `stance`) and a mandatory `run()` loop.
- **`JudgeAgent` (The Father)**: Orchestrates the debate, manages multiprocessing pipes, calculates scores, and delivers final judgments.
- **`DebaterAgent` (The Children)**: Process-isolated agents that generate arguments based on their unique personas and stances.

### Personas & Stances
1. **Dr. Aris Thorne (Ethics Researcher)**: Cautious stance. Focuses on safety, risk mitigation, and regulatory frameworks.
2. **Alex Vanguard (Tech Entrepreneur)**: Optimistic stance. Focuses on innovation, market-driven solutions, and ROI.
3. **Justice P. Vane (Policy Expert)**: Balanced stance. Acts as the Judge, synthesizing multiple viewpoints into an evidence-based middle ground.

### Communication & IPC
- **Standard Multiprocessing**: Each agent runs in its own OS-level process.
- **JSON Protocol**: All messages are serialized as JSON payloads to ensure structured data exchange.
- **Sequential Routing**: A strict `parent -> child -> parent` flow ensures the Judge maintains total control over the context and debate history.

## 3. Implemented Features

### Advanced Scoring Mechanism
The Judge evaluates every response based on:
- **Depth**: Points equal to the word count.
- **Quality Keywords**: +2 bonus points for terms like *evidence, research, data, study, however, therefore, because, consider*.

### Memory & Persistence
- **`memory/MEMORY.md`**: Stores turn-by-turn summaries to ensure the Judge doesn't lose context during long debates.
- **`results/results.md`**: Stores final session reports, including Session IDs, scores, and detailed logical explanations for the winner.
- **Tie-Breaker**: A mechanism that reviews stored summaries to decide a winner if scores are identical after 10 rounds.

### Prompt Engineering
- **Persona Enforcement**: System instructions mandate that agents stay strictly in character.
- **Constraint Logic**: Responses must be concise (1-3 arguments), include 2 examples, and avoid conversational filler.
- **Tone Control**: Explicitly enforces a polite, respectful, and "Politically Correct" tone.

### UI & Configuration
- **Terminal Menu**: A simplified keyboard-driven menu (`src/my_package/ui/terminal_menu.py`) for starting the debate.
- **Fixed Topic**: The debate topic is hardcoded to: *"Do social media algorithms do more harm to democratic discourse than good?"*
- **Auto-Cleanup**: Temporary memory is automatically wiped after each session report is saved.

## 4. Operational Parameters
- **Debate Length**: 10 Rounds (20 total responses).
- **Timeouts**: 1-minute maximum response time per agent.
- **Rule Injection**: Mandatory rule schemas are stored and enforced via `config/setup.json`.

---
*Last Updated: Wednesday, May 27, 2026*
