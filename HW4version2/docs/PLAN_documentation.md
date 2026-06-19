---
title: PLAN — Project Documentation Implementation
version: "1.00"
status: approved
---

# PLAN — Project Documentation Implementation

## Execution Order

Task 9 (PRD/PLAN/TODO) → Task 10 (tools.md) → Task 11 (agents.md) → Task 12 (pipeline.md) → Task 13 (commit)

No dependency between tools.md, agents.md, pipeline.md — they can be written in any order
but pipeline.md references both agents and tools so it is best written last.

---

## tools.md Structure

Each tool gets a level-2 heading (`## Tool N: <Registered Name>`), then subsections:

```
### What it does
### Parameters
| Name | Type | Default | Description |
### Returns
### Used by
### When it is called
```

Source of truth: `src/hw4/crewai_tools/tools.py`

**Tool 1 — Load Graph Metrics**
- Reads `graph.json` produced by Grphify
- Computes degree centrality using Counter over edge source/target
- Builds a NetworkX DiGraph to count bridges
- Returns JSON: node_count, edge_count, community_count, bridge_count, top_20_hubs, edge_type_counts
- Used by: Graph Navigator (primary), Architect Detective (secondary), Quality Gate (after-fix check)

**Tool 2 — Read Obsidian Navigation Files**
- Reads `hot.md` and `index.md` from the Obsidian vault
- Truncates each to max_chars (default 2000) to stay token-efficient
- Returns JSON dict: `{ "hot.md": "...", "index.md": "..." }`
- Used by: Graph Navigator only

**Tool 3 — Read Source File Snippet**
- Reads any Python source file by path
- Truncates to max_chars (default 1500) — enforces token discipline
- Returns raw file content as string, or "File not found: ..." if missing
- Used by: Fix Strategist only — reads the hot file before proposing a refactor

**Tool 4 — Run Unit Tests**
- Runs `uv run pytest tests/unit -q --cov=src --cov-report=term-missing`
- Parses TOTAL line to extract coverage %
- Returns JSON: `{ "passed": bool, "coverage_percent": float, "output_tail": str }`
- Used by: Quality Gate only — called after the fix is committed

---

## agents.md Structure

Each agent gets a level-2 heading (`## Agent N: <Role>`), then subsections:

```
### Role
### Goal
### Backstory
### Tools available
### Input context
### Output
### Passes to
```

Source of truth: `src/hw4/crewai_agents/agents.py` + `src/hw4/crewai_tasks/tasks.py`

**Agent 1 — Graph Navigator**
- Tools: Load Graph Metrics + Read Obsidian Navigation Files
- Task: graph_summary_task (no context dependency — first in chain)
- Output file: `results/v2_graph_summary.json`
- Passes to: Architect Detective via context=[graph_summary_task]

**Agent 2 — Architect Detective**
- Tools: Load Graph Metrics (can re-query if needed)
- Task: bug_detection_task (context=[graph_summary_task])
- Receives: graph summary with top hubs and metrics
- Output file: `results/v2_bugs.json`
- Passes to: Fix Strategist via context=[graph_summary_task, bug_detection_task]

**Agent 3 — Fix Strategist**
- Tools: Read Source File Snippet
- Task: fix_proposal_task (context=[graph_summary_task, bug_detection_task])
- Receives: graph summary + bug list; reads hot file snippet itself
- Output file: `results/v2_fix_proposal.json`
- Passes to: Quality Gate via context=[graph_summary_task, bug_detection_task, fix_proposal_task]
- On retry: backstory gets patched with retry_instruction from previous FAIL verdict

**Agent 4 — Quality Gate**
- Tools: Run Unit Tests + Load Graph Metrics
- Task: verification_task (context=[graph_summary_task, bug_detection_task, fix_proposal_task])
- Receives: full context (summary + bugs + proposal)
- Output file: `results/v2_verification.json`
- Returns: verdict PASS or FAIL + retry_instruction if FAIL

---

## pipeline.md Structure

```
# Pipeline Architecture

## Overview (ASCII diagram)
## Stage 1 — Grphify
## Stage 2 — CrewAI Agents
### Task context chaining
### Agent sequence
### Retry loop
## Stage 3 — GenericFixApplier
## Stage 4 — VerifyService
## Data flow table
## ApiGatekeeper — wrapping every external call
## How to read this codebase in 5 minutes
```

**Key points to cover:**

Context chaining: CrewAI `context=[task_a, task_b]` means task_b's agent automatically
receives task_a's full output in its prompt. The agent does not need to call any tool to
get that information — CrewAI injects it. This is what makes the pipeline memory-efficient.

Retry loop (in `CrewRunnerV2.run()`):
1. Crew kicks off all 4 tasks in sequence
2. After kickoff, `v2_verification.json` is read
3. If `verdict == "PASS"` → stop
4. If `verdict == "FAIL"` → append `retry_instruction` to fix_strategist.backstory → re-run
5. Maximum 2 attempts (MAX_RETRIES = 2)

Data artifacts table:

| Stage | Consumes | Produces |
|-------|----------|----------|
| 1 Grphify | `data/cookiecutter/` | `artifacts/graph.json`, `artifacts/graph.html`, `artifacts/hot.md`, `artifacts/index.md` |
| 2 Agents | `artifacts/graph.json`, `artifacts/hot.md` | `results/v2_graph_summary.json`, `results/v2_bugs.json`, `results/v2_fix_proposal.json`, `results/v2_verification.json` |
| 3 Fix Applier | `results/v2_fix_proposal.json`, target source file | Modified source file, new module, `results/fix_diff.patch` |
| 4 Verify | Modified source, `artifacts/graph.json` | `artifacts/graph_after.json`, `results/metrics_comparison.json`, `reports/verification.md` |
