---
title: PLAN — Agents Stage
version: "1.00"
status: draft
---

# Agents Stage Plan

## Goal
Build 4 CrewAI agents, each in its own file, and wire them into a crew
that reads the graph and produces structured JSON results.

## Prerequisites
- Grphify stage complete
- `artifacts/graph.json` exists
- `GraphMetrics` dataclass available

## Agent Files (one agent per file)

```
src/hw4/agents/
├── graph_reader.py        ← Agent 1
├── bug_detector_agent.py  ← Agent 2
├── fix_proposer.py        ← Agent 3
└── verifier.py            ← Agent 4
```

## Steps

### 1. Agent 1 — `graph_reader.py`
Reads `artifacts/graph.json` and returns a compact graph summary.
Never passes the full raw graph to the LLM — only computed stats.

### 2. Agent 2 — `bug_detector_agent.py`
Receives the graph summary and uses the LLM to identify architectural bugs
(SPOFs, overloaded hubs, weak bridges). Returns a structured bug list.

### 3. Agent 3 — `fix_proposer.py`
Receives the bug list. Reads only the affected file (not the full codebase)
and proposes a concrete fix for each bug.

### 4. Agent 4 — `verifier.py`
Applies the fix, re-runs Grphify, runs unit tests, and compares
before/after graph metrics. Returns a verification report.

### 5. `crew_runner.py` — assemble the crew
File: `src/hw4/services/crew_runner.py`

Wires all 4 agents into a `crewai.Crew` with sequential process.
All LLM calls go through `ApiGatekeeper`.

### 6. Write unit tests
One test file per agent under `tests/unit/`.
Use mock inputs — no real LLM calls in unit tests.

## Done Checklist
- [ ] All 4 agent files created, each under 150 lines
- [ ] `crew_runner.py` assembles and runs the crew
- [ ] All agent outputs are valid JSON
- [ ] All unit tests pass
- [ ] Zero Ruff errors

## Git Commit
```
feat: add CrewAI agents — graph reader, bug detector, fix proposer, verifier
```

## Next
`PLAN_bug_fix.md` — bug detection algorithm and fix application
