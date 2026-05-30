# PRD — Debate Logger & Watchdog

---

## Part 1: DebateLogger

### Role
Provides structured, rotating file logs for every event in the debate system.
Exists to give the instructor a verifiable, timestamped audit trail and to
produce the cost table data that populates the README.

### Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Log message | str | Any class | Human-readable event description |
| Log level | str | Caller | INFO, WARN, ERROR |
| Structured data | dict | Gatekeeper | Token counts, costs, API metadata |
| Logging config | dict | logging_config.json | max_files, max_lines, log_dir, format |

### Outputs

| Output | Type | Destination | Description |
|--------|------|-------------|-------------|
| Log file | .log file | config log_dir | Structured lines: timestamp | level | source | message |
| Rotated archive | .log file | log_dir | Old file closed when line limit hit; new file opened |

### Rotation Strategy (FIFO)
- Max files: 20 (from config)
- Max lines per file: 500 (from config)
- When line limit hit: close current file, open new file with incremented index
- When file count exceeds max: delete oldest file (FIFO — first in, first out)
- File naming: `debate_YYYYMMDD_HHMMSS_NNN.log`

### Constraints
- Logger must never block the calling thread — writes are synchronous but fast
- Log directory created automatically if missing
- Log format defined in logging_config.json — not hardcoded

### Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Log directory missing | Create on first write; log warning to stderr |
| Disk full | Catch OSError; print to stderr; do not crash the debate |
| Concurrent writes from multiple processes | Use multiprocessing.Lock on file handle |
| Log line exceeds 500 chars | Truncate with `...[truncated]` suffix |

### Success Criteria
- File count never exceeds max_files config value
- Line count per file never exceeds max_lines config value
- Every Gatekeeper call produces a log entry with token counts
- Log files parseable as structured data (pipe-delimited)

---

## Part 2: Watchdog

### Role
Monitors all three debate processes (Father, Pro, Con) and restarts any that die.
Exists because a crashed child should not end the entire debate — resilience
is an engineering requirement.

### Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Process list | list[Process] | SDK / main | Managed multiprocessing.Process objects |
| Keepalive config | dict | setup.json | Check interval (seconds), max restarts per process |
| Restart factory | callable | SDK | Function that creates a fresh process for a given role |

### Outputs

| Output | Type | Destination | Description |
|--------|------|-------------|-------------|
| Restart event | log entry | DebateLogger | Which process died, when, restart attempt number |
| Keepalive ping | log entry | DebateLogger | Periodic heartbeat confirming processes are alive |
| Fatal alert | stderr + log | CLI / operator | Emitted when max_restarts exceeded for a process |

### Constraints
- Restart must complete within 5 seconds (from config)
- Max 3 restarts per process per run (configurable)
- Watchdog runs as a daemon process — dies when main process exits
- Keepalive check interval: configurable (default 2 seconds)
- Watchdog must NOT interfere with message queues — only manages process lifecycle

### Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| No watchdog | Single process death ends entire debate — fails resilience requirement |
| Thread-based watchdog | Cannot restart a process from a thread reliably on all OS |
| Supervisor process (external) | Adds external dependency; Python multiprocessing sufficient for this scope |

### Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Process won't restart (3 failures) | Log fatal; halt debate gracefully; print final partial results |
| All 3 processes die simultaneously | Watchdog detects all dead; logs panic; exits with error code 1 |
| Zombie process (exits but not joined) | Watchdog calls proc.join(timeout=1) before restart |
| Father process dies | Critical — Watchdog logs CRITICAL and halts (no Father = no debate) |

### Success Criteria
- Simulated process kill in integration test triggers restart within 5 seconds
- Restart count logged accurately
- After restart, debate resumes from last known round (state passed via queue)
