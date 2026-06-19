# Agents Reference

This file documents every CrewAI agent in the EX04 pipeline. All agent definitions live in
`src/hw4/crewai_agents/agents.py`. Agents are built by `build_agents()` and run inside
`CrewRunnerV2.run()` via a `Crew` with `Process.sequential`.

Each agent has a **role**, a **goal** (what it must accomplish), a **backstory** (the constraints
and personality that shape its reasoning), a set of **tools** it can call, and a defined
**output** that the next agent in the chain receives automatically via CrewAI's `context=` system.

## How agents communicate

CrewAI injects the full output of a previous task into the next agent's prompt automatically.
This means agents do not call each other directly — they receive context through their task
definitions. See [pipeline.md](pipeline.md) for the full context-chaining diagram.

## Agent Relationship Overview

```
┌─────────────────────┐
│   Graph Navigator   │ ← Task 1 (no context input)
│  graph_summary_task │
└────────┬────────────┘
         │ context injected
         ▼
┌─────────────────────┐
│ Architect Detective │ ← Task 2 (receives graph summary)
│  bug_detection_task │
└────────┬────────────┘
         │ context injected
         ▼
┌─────────────────────┐
│   Fix Strategist    │ ← Task 3 (receives summary + bugs)
│  fix_proposal_task  │
└────────┬────────────┘
         │ context injected
         ▼
┌─────────────────────┐
│    Quality Gate     │ ← Task 4 (receives summary + bugs + proposal)
│  verification_task  │
└─────────────────────┘
```

---

## Agent 1: Graph Navigator

**Role title:** Graph Navigator  
**Task:** `graph_summary_task`  
**Output file:** `results/v2_graph_summary.json`

### Goal

Load the code dependency graph and produce a precise structural summary of the top
architectural hot-spots: which nodes have the most connections (hubs), how many
communities exist, how many bridge edges there are, and a two-sentence architectural
interpretation of what the graph is telling us about the codebase design.

### Backstory

> "You are a software architect who specialises in dependency-graph analysis. You never
> read entire source files — you navigate the graph first, identify the most connected
> nodes, and report exactly what the next agent needs. Token efficiency is your core
> discipline."

The backstory is critical: it prevents the agent from reaching for source files when
it doesn't need them. Everything it needs is in the graph and the Obsidian navigation
files.

### Tools available

| Tool | Why this agent needs it |
|------|------------------------|
| `Load Graph Metrics` | Primary source: computes node/edge counts, hub rankings, bridge count |
| `Read Obsidian Navigation Files` | Secondary source: adds human-readable context from `hot.md` and `index.md` |

### Input context

None — this is the **first task** in the chain. The agent starts with only the path to
`artifacts/graph.json` and the Obsidian vault directory, both injected via the task description.

### Output

A JSON object saved to `results/v2_graph_summary.json`:

```json
{
  "node_count": 278,
  "edge_count": 517,
  "community_count": 15,
  "bridge_count": 127,
  "top_10_hubs": [
    ["exceptions_undefinedvariableintemplate", 21],
    ["exceptions_cookiecutterexception", 20],
    ...
  ],
  "interpretation": "The exceptions module is a central coordination hub..."
}
```

### Passes to

**Architect Detective**, **Fix Strategist**, and **Quality Gate** — all three receive the
graph summary in their context via `context=[graph_summary_task, ...]`. The Quality Gate
specifically reads `top_10_hubs[0][1]` (the top hub degree) to compute the estimated
improvement after the fix.

---

## Agent 2: Architect Detective

**Role title:** Architect Detective  
**Task:** `bug_detection_task`  
**Output file:** `results/v2_bugs.json`

### Goal

Classify every node with degree > 10 as a HUB, every node whose removal would disconnect
the graph as a SPOF (Single Point of Failure), and every bridge edge as a WEAK_BRIDGE.
Rank all discovered bugs by severity (HIGH if degree > 15, MEDIUM otherwise) and return
a structured JSON list of up to 5 bugs.

### Backstory

> "You are a forensic software architect. You receive a graph summary and apply systematic
> structural rules to detect defects. You output a JSON list of bugs, each with bug_type,
> node_name, source_file, severity, and a one-sentence explanation grounded in the graph
> data you received."

The detective persona enforces that findings must be **evidence-based** — every bug
explanation must cite a specific degree value or connectivity fact from the graph summary,
not generic statements.

### Bug detection rules

| Rule | Condition | Severity |
|------|-----------|----------|
| HUB | `degree > 10` | HIGH if `degree > 15`, MEDIUM otherwise |
| SPOF | Node in top 15 by degree AND its removal disconnects the graph | HIGH |
| WEAK_BRIDGE | Bridge edge connecting otherwise separate communities | MEDIUM |

### Tools available

| Tool | Why this agent needs it |
|------|------------------------|
| `Load Graph Metrics` | Can re-query the graph to verify specific degree values if needed |

In practice the agent usually reasons from the graph summary it received in context and
does not need to call the tool — but the tool is available for verification.

### Input context

Receives `graph_summary_task` output automatically via `context=[graph_summary_task]`.
This means the agent's prompt already contains the full JSON graph summary without any
tool call needed.

### Output

A JSON array saved to `results/v2_bugs.json`, ranked HIGH first:

```json
[
  {
    "bug_type": "HUB",
    "node_name": "exceptions_undefinedvariableintemplate",
    "source_file": "exceptions.py",
    "severity": "HIGH",
    "explanation": "Node has degree 21, exceeding the HUB threshold of 10 — it is imported by 21 other symbols."
  },
  {
    "bug_type": "HUB",
    "node_name": "exceptions_cookiecutterexception",
    "source_file": "exceptions.py",
    "severity": "HIGH",
    "explanation": "Node has degree 20..."
  }
]
```

### Passes to

**Fix Strategist** and **Quality Gate** via `context=[graph_summary_task, bug_detection_task]`.

---

## Agent 3: Fix Strategist

**Role title:** Fix Strategist  
**Task:** `fix_proposal_task`  
**Output file:** `results/v2_fix_proposal.json`

### Goal

For the highest-severity HUB bug, read the relevant source file snippet and propose a
concrete structural refactor: which file to change (`target_file`), what to extract into
a new module (`new_module_name`), a precise description of what logic to move
(`change_description`), why this reduces coupling (`rationale`), and an integer estimate
of how much the hub's degree will drop after the fix (`estimated_degree_reduction`).

If a previous fix attempt returned a FAIL verdict, the agent must address the
`retry_instruction` from that verdict explicitly in its new proposal.

### Backstory

> "You are a senior refactoring engineer. You receive a bug list and graph context. You
> read only the hot file — never the full repo. You produce one FixProposal with a
> target_file, new_module_name, change_description, rationale, and an estimate of how
> much the hub degree will drop after the refactor."

The "read only the hot file" constraint is key — it enforces token discipline. The agent
inspects exactly one file before proposing a fix.

**On retry:** `CrewRunnerV2` appends the failure reason directly to this agent's `backstory`
field before the crew re-runs:

```python
agents["fix_strategist"].backstory += (
    f" NOTE — attempt {attempt} failed: {retry_instruction}. "
    "Adjust your proposal to address this before making any new suggestion."
)
```

### Tools available

| Tool | Why this agent needs it |
|------|------------------------|
| `Read Source File Snippet` | Reads the first 1500 characters of the hot file to understand its structure before proposing the refactor |

### Input context

Receives `graph_summary_task` + `bug_detection_task` outputs via
`context=[graph_summary_task, bug_detection_task]`. The agent sees:
- The full graph metrics
- The ranked bug list with source file paths
- (On retry) the failure reason in its backstory

### Output

A JSON object saved to `results/v2_fix_proposal.json`:

```json
{
  "bug": {
    "bug_type": "HUB",
    "node_name": "exceptions_undefinedvariableintemplate",
    "source_file": "exceptions.py",
    "severity": "HIGH"
  },
  "target_file": "data/cookiecutter/cookiecutter/exceptions.py",
  "new_module_name": "template_exceptions.py",
  "change_description": "Move UndefinedVariableInTemplate class out of exceptions.py into a new template_exceptions.py module. Update all imports.",
  "rationale": "UndefinedVariableInTemplate is Jinja2-specific and unrelated to the base exception hierarchy. Separating it reduces the degree of exceptions.py from 21 to ~14.",
  "estimated_degree_reduction": 7
}
```

**Important:** `target_file` must be the **full relative path** from project root
(e.g., `data/cookiecutter/cookiecutter/exceptions.py`), not just a filename. The
`GenericFixApplier` uses this path directly to open and rewrite the file.

### Passes to

**Quality Gate** via `context=[graph_summary_task, bug_detection_task, fix_proposal_task]`.
The Quality Gate reads `estimated_degree_reduction` to compute `metrics_improved`.

---

## Agent 4: Quality Gate

**Role title:** Quality Gate  
**Task:** `verification_task`  
**Output file:** `results/v2_verification.json`

### Goal

Verify that the proposed fix actually improves the codebase. Run unit tests to check
that nothing is broken and coverage is still ≥ 85%. Compute the estimated graph
improvement from the fix proposal. Produce a PASS or FAIL verdict. A FAIL must include
a specific `retry_instruction` telling the Fix Strategist exactly what to change.

### Backstory

> "You are a CI/CD quality enforcer. You run tests, check metrics, and deliver a clear
> verdict. PASS requires: tests green, coverage >= 85%, and at least one graph metric
> improved vs the before-fix baseline. A FAIL verdict includes exactly what went wrong
> and what the Fix Strategist must change."

The "CI/CD enforcer" persona makes the agent strict: it cannot give a PASS on partial
evidence. It must verify all three conditions explicitly.

### PASS conditions (all three required)

| Condition | How verified |
|-----------|-------------|
| `tests_passed == true` | `Run Unit Tests` tool returns `"passed": true` |
| `coverage_percent >= 85` | `Run Unit Tests` tool returns `coverage_percent >= 85.0` |
| `metrics_improved == true` | `estimated_degree_reduction > 0` from the fix proposal context |

### Tools available

| Tool | Why this agent needs it |
|------|------------------------|
| `Run Unit Tests` | Runs `uv run pytest` to verify tests pass and coverage ≥ 85% |
| `Load Graph Metrics` | Can optionally query the after-fix graph to compare hub counts |

### Input context

Receives all three previous task outputs via
`context=[graph_summary_task, bug_detection_task, fix_proposal_task]`:
- `top_10_hubs[0][1]` from graph summary → `top_hub_degree_before`
- `estimated_degree_reduction` from fix proposal → computes `top_hub_degree_after_estimate`
- Bug list for context

### Output

A JSON object saved to `results/v2_verification.json`:

```json
{
  "verdict": "PASS",
  "tests_passed": true,
  "coverage_percent": 93.0,
  "metrics_improved": true,
  "metrics_delta": {
    "top_hub_degree_before": 21,
    "estimated_degree_reduction": 7,
    "top_hub_degree_after_estimate": 14
  },
  "failure_reason": null,
  "retry_instruction": null
}
```

On FAIL:

```json
{
  "verdict": "FAIL",
  "tests_passed": false,
  "coverage_percent": 72.0,
  "metrics_improved": true,
  "failure_reason": "Tests failed — 3 tests broke after the refactor.",
  "retry_instruction": "The refactor broke import paths. Ensure all callers of UndefinedVariableInTemplate are updated to import from template_exceptions instead of exceptions."
}
```

### Passes to

Nothing — this is the **last task** in the chain. Its output is read by `CrewRunnerV2.run()`
after the crew finishes. If `verdict == "FAIL"`, the runner injects `retry_instruction`
into the Fix Strategist's backstory and re-runs the entire crew (up to `MAX_RETRIES = 2`).
