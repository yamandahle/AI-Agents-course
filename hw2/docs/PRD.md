#  Product Requirements Document (PRD) - Exercise 02

## 1. Project Overview
The objective of this project is to build an autonomous, multi-agent AI debate platform controlled entirely by a deterministic Python orchestration layer. The system will manage two opposing debater agents (Proponent and Opponent) and an independent Judge agent to simulate a complete, structured rhetorical debate session without user intervention.

---

## 2. Functional Requirements

### Debate Flow Control & Rules
* **No Direct Communication**: Debater processes are strictly forbidden from passing text directly to one another. All communication loops must route exclusively through the Judge process relay (`Debater A ──> Judge ──> Debater B`).
* **Turn Depth Benchmark**: The system must execute a minimum constraint of **10 continuous pings** (one argument and one counter-argument turn) per side.
* **No-Tie Verdict Directive**: The Judge agent cannot declare a draw, split decision, or tie. It must name a definitive winner based entirely on rhetorical persuasiveness and citation handling.
* **Anti-Collusion Mechanism**: The system must actively prevent the debaters from agreeing with each other. If soft validation flags reveal a loss of friction, the Judge must intervene to restore contradiction.

###  Integrated Grounding Tools
* **Web Search Engine**: Each debater agent must be given an integrated web-search capability to look up live data online and ground its arguments with real-world citations.

### User Interface Requirements
* **Keyboard-Driven Terminal UI**: The entry point must feature an interactive, menu-driven terminal interface operated via keyboard keys. It must allow users to choose topics, adjust limits, or launch the multi-process sequence.

---

## 3. Non-Functional & Engineering Safety Requirements

###  Concurrency & Guardrails
* **Independent Processes**: Each agent must run as an isolated operating system process (`multiprocessing`), utilizing thread-safe queues or pipes for Inter-Process Communication (IPC).
* **Background Watchdog Timer**: A background thread must monitor response delays. If any process hits a frozen API call or hangs beyond the timeout threshold, the watchdog must forcefully terminate it via `os.kill` and spin up a replacement.
* **First-In, First-Out (FIFO) Log Rotation**: Telemetry data must split across an automated rotating log handler, strictly capped at **500 lines per file** with a hard safety limit on total backup files to protect local disk space.

###  Security & Architecture Configuration
* **Decoupled Parameters**: No hardcoded values are allowed in code strings. Settings must load dynamically from a static `config/setup.json` file.
* **Secret Vault Isolation**: Private API credentials must be stored locally inside a hidden `.env` file and never committed to GitHub.

---

## 4. Final Deliverables & Success Criteria
* **Passing Test Suite**: 100% test coverage validating JSON protocols, Watchdog interrupts, and FIFO line limits.
* **Unpolluted Context State**: The active debate history must be written line-by-line using a `.jsonl` file to allow seamless context engineering and error-recovery passes.
* **Human-Readable Transcript**: A structured `.md` log file logging the clean dialogue transcript, queries, and final score matrix for human review.
* **Statistical Performance Dashboard**: A persistent cross-session ledger to catch runtime stagnation and record historical win/loss ratios.

---

## 5. Human Checkpoint & Bias Analytics Engine (Audit Track)

To allow developers and graders to detect if agents are differentiating their arguments effectively, or if the Judge exhibits a deterministic positional bias, the system must implement a post-debate telemetry audit:

### A. Positional Win-Rate Tracker
* **The Analytics Ledger**: The system will maintain a persistent data file on disk (`outputs/analytics/win_loss_matrix.json`). Every time a debate concludes, the main process must parse the Judge's final decision packet and increment the scoreboards.
* **Bias Detection Metrics**: The file will maintain cumulative integers tracking:
  ```json
  {
    "total_debates_run": 12,
    "proponent_wins": 10,
    "opponent_wins": 2,
    "detected_bias_risk": "HIGH_PROPONENT_BIAS"
  }
