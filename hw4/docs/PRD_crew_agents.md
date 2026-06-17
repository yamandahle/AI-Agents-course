---
title: PRD — CrewAI Multi-Agent Workflow
version: "1.00"
status: draft
---

# PRD — CrewAI Agent Crew

## 1. Purpose

This document covers the multi-agent crew design: which agents exist, what each one does,
how they communicate, and how token efficiency is maintained.

## 2. Agent Roster

### Agent 1 — GraphReaderAgent
- **Role:** Load and summarize `graph.json`
- **Input:** `artifacts/graph.json`
- **Output:** Graph summary JSON (node count, top hubs, communities, bridges)
- **Token rule:** Never pass the full graph to an LLM. Compute stats in Python; pass only summary.

### Agent 2 — BugDetectorAgent
- **Role:** Identify architectural bugs in the graph summary
- **Input:** Graph summary from Agent 1
- **Output:** List of `ArchitecturalBug` objects (type, node, severity, explanation)
- **Detects:** SPOFs, overloaded hubs (degree > threshold), weak bridges

### Agent 3 — FixProposerAgent
- **Role:** Propose concrete code-level fixes for each detected bug
- **Input:** List of `ArchitecturalBug` objects + relevant file excerpts (not full files)
- **Output:** `FixProposal` objects (which file, what change, rationale)
- **Token rule:** Pass only the affected file(s), not the entire codebase

### Agent 4 — VerifierAgent
- **Role:** Apply fix, re-run Grphify, run unit tests, compare before/after metrics
- **Input:** `FixProposal` objects + original graph metrics
- **Output:** `VerificationReport` (pass/fail, metric delta, test results)

## 3. Workflow Diagram

```
graph.json
    │
    ▼
[GraphReaderAgent] ──→ graph_summary.json
                                │
                                ▼
                    [BugDetectorAgent] ──→ bugs.json
                                                │
                                                ▼
                                    [FixProposerAgent] ──→ fix_proposal.json
                                                                    │
                                                                    ▼
                                                        [VerifierAgent] ──→ verification.json
```

## 4. Token Efficiency Rules

| Rule | Reason |
|------|--------|
| Never pass `graph.json` (can be >100k tokens) | LLM context limit + cost |
| Never pass full source files | Same reason |
| Pass only top-N nodes (configurable, default 20) | Captures most important structure |
| Use Python to compute stats before LLM call | Free computation vs expensive tokens |
| Keep each agent prompt < 2000 tokens | Avoid "lost in the middle" forgetting |

## 5. Data Models

```
ArchitecturalBug:
  - bug_type: "SPOF" | "HUB" | "WEAK_BRIDGE"
  - node_name: str
  - severity: "HIGH" | "MEDIUM" | "LOW"
  - explanation: str

FixProposal:
  - bug: ArchitecturalBug
  - target_file: str
  - change_description: str
  - rationale: str

VerificationReport:
  - fix_applied: bool
  - tests_passed: bool
  - centrality_delta: float  # negative = improvement
  - summary: str
```

## 6. Configuration (from `config/setup.json`)

```json
{
  "agents": {
    "top_n_nodes": 20,
    "max_prompt_tokens": 2000,
    "hub_degree_threshold": 10,
    "spof_removal_test": true
  }
}
```

## 7. Success Criteria

- All 4 agents complete without error
- At least 1 bug detected and reported
- Fix proposal is concrete (names a file and a change)
- Verification report shows test pass status
- All agent results saved to `results/`
