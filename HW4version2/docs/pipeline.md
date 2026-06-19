# Pipeline Architecture

This document explains how the EX04 pipeline works end-to-end — from scanning a Python
codebase to detecting architectural bugs, applying an LLM-generated fix, and verifying
the result. No source code reading required: everything is explained here.

---

## How to Read This Codebase in 5 Minutes

1. **Entry point:** `run_pipeline.py` — 4 print blocks, 4 SDK calls. Read this first.
2. **SDK:** `src/hw4/sdk/sdk.py` — the single public interface. All logic flows through here.
3. **Agents:** `src/hw4/crewai_agents/agents.py` — 4 agents, each with a role and tools.
4. **Tasks:** `src/hw4/crewai_tasks/tasks.py` — 4 tasks wired with `context=` chains.
5. **Tools:** `src/hw4/crewai_tools/tools.py` — 4 stateless functions agents can call.
6. **Results:** `results/v2_*.json` — one JSON file per agent output.

Everything else (services, shared, models) is infrastructure supporting these six files.

---

## Top-Level Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                        run_pipeline.py                               ║
║                                                                      ║
║  Stage 1          Stage 2             Stage 3         Stage 4        ║
║  ─────────        ────────────────    ───────────     ──────────     ║
║  Grphify    →    CrewAI Agents    →   Fix Applier  →  Verify        ║
║  (graph          (4 agents,           (LLM writes     (pytest +      ║
║   builder)        sequential,          code, git       ruff +        ║
║                   retry loop)          commit)         graph rescan) ║
╚══════════════════════════════════════════════════════════════════════╝
                         ▲
                 ApiGatekeeper wraps
                 every external call
                 (rate limits, retry)
```

---

## Stage 1 — Grphify: Build the Code Graph

**Code:** `sdk.run_grphify()` → `GraphBuilderService`  
**Input:** `data/cookiecutter/cookiecutter/` (18 Python files)  
**Output:** `artifacts/graph.json`, `artifacts/graph.html`, `artifacts/hot.md`, `artifacts/index.md`

Grphify is an external CLI tool that performs **static AST analysis** of Python code.
It scans every `.py` file, extracts function definitions, class definitions, and import
relationships, and outputs a JSON graph where:

- **Nodes** = Python symbols (functions, classes, modules)
- **Edges** = dependency relationships (calls, imports, inheritance)
- **Edge types:** Extracted (certain), Inferred (probable), Ambiguous (needs review)

After the graph is built, Grphify syncs to an **Obsidian vault** (`obsidian/`), generating:
- `hot.md` — list of the most-connected nodes, sorted by degree (the "hot files")
- `index.md` — table of contents of all communities/modules in the vault

**Why scan only the package, not the full repo?**  
Scanning `cookiecutter/cookiecutter/` (18 files) instead of the full repository
gives a focused graph of 278 nodes / 517 edges. Scanning the full repo produces
1264 nodes — too noisy for meaningful hub detection.

---

## Stage 2 — CrewAI Agents: Analyse and Propose

**Code:** `CrewRunnerV2.run()`  
**Input:** `artifacts/graph.json`, `obsidian/hot.md`, `obsidian/index.md`  
**Output:** `results/v2_graph_summary.json`, `results/v2_bugs.json`, `results/v2_fix_proposal.json`, `results/v2_verification.json`

This stage runs **4 CrewAI agents in sequence**, each building on the previous agent's
output. The crew uses `Process.sequential` — tasks run one after another, not in parallel.

### Task Context Chaining

The key mechanism is CrewAI's `context=` parameter on each `Task`. When a task has
`context=[task_a, task_b]`, CrewAI automatically **injects the full output of task_a and
task_b into the agent's prompt** before the agent starts reasoning.

This means agents do not need to call tools to read what previous agents found —
they receive that information for free in their context window.

```
graph_summary_task  (no context)
        │
        │ full JSON output injected
        ▼
bug_detection_task  (context=[graph_summary_task])
        │
        │ both outputs injected
        ▼
fix_proposal_task   (context=[graph_summary_task, bug_detection_task])
        │
        │ all three outputs injected
        ▼
verification_task   (context=[graph_summary_task, bug_detection_task, fix_proposal_task])
```

### Agent Sequence (Task-by-Task)

#### Task 1 — graph_summary_task → Graph Navigator

The Graph Navigator calls `Load Graph Metrics` on `artifacts/graph.json` and
`Read Obsidian Navigation Files` on `obsidian/`. It combines the structural metrics
(node count, hub ranking, bridge count) with the narrative context from `hot.md`
and produces a concise summary JSON.

**Token cost:** ~645 tokens (vs ~23,537 if all source files were sent directly).

#### Task 2 — bug_detection_task → Architect Detective

The Architect Detective **receives the graph summary in its context** without making
any tool call. It applies fixed rules to classify bugs:
- Degree > 10 → HUB (HIGH if degree > 15, MEDIUM otherwise)
- Removal disconnects graph → SPOF
- Bridge edge between communities → WEAK_BRIDGE

It returns a ranked JSON list of up to 5 bugs.

#### Task 3 — fix_proposal_task → Fix Strategist

The Fix Strategist **receives the graph summary and bug list in its context**. It picks
the highest-severity HUB bug, calls `Read Source File Snippet` to read the first 1500
characters of the bug's source file, and proposes a concrete refactor:
- Which file to modify (`target_file` — full relative path)
- What new module to create (`new_module_name`)
- What logic to move (`change_description`)
- Why this reduces coupling (`rationale`)
- Estimated degree reduction (`estimated_degree_reduction`)

#### Task 4 — verification_task → Quality Gate

The Quality Gate **receives all three previous outputs in its context**. It:
1. Calls `Run Unit Tests` to check if tests pass and coverage ≥ 85%
2. Reads `top_10_hubs[0][1]` from the graph summary (top hub degree before fix)
3. Reads `estimated_degree_reduction` from the fix proposal
4. Computes `top_hub_degree_after_estimate = before - reduction`
5. Sets `metrics_improved = (estimated_degree_reduction > 0)`
6. Issues `verdict: PASS` if all three conditions are met, `FAIL` otherwise

### The Retry Loop

`CrewRunnerV2.run()` wraps the crew kickoff in a loop with `MAX_RETRIES = 2`:

```
Attempt 1:
  crew.kickoff()           ← all 4 tasks run
  read v2_verification.json
  verdict == "PASS"?  ─── yes ──→ break, return results
       │
       no
       ▼
  Inject retry_instruction into fix_strategist.backstory:
    "NOTE — attempt 1 failed: <why>. Adjust your proposal..."

Attempt 2:
  crew.kickoff()           ← all 4 tasks re-run, Fix Strategist now knows what failed
  read v2_verification.json
  verdict == "PASS"?  ─── yes ──→ break, return results
       │
       no
       ▼
  Exit loop (MAX_RETRIES exhausted), return whatever was last written
```

**What changes on retry:** Only the Fix Strategist's `backstory` is modified — the failure
reason from the Quality Gate is appended. All other agents are unchanged. The next attempt
re-runs the full task chain, so the Fix Strategist sees the corrected backstory and
produces a different proposal.

---

## Stage 3 — GenericFixApplier: Write and Commit the Fix

**Code:** `sdk.apply_fix()` → `GenericFixApplier.apply_from_proposal()`  
**Input:** `results/v2_fix_proposal.json`, target source file  
**Output:** Modified source file, new module file, `results/fix_diff.patch`, new git branch

This stage runs **outside the CrewAI agent loop** — it is a separate Python service
triggered by `run_pipeline.py` after the agents complete.

The applier:
1. Reads `v2_fix_proposal.json` (strips markdown fences if the LLM wrapped in ```)
2. Resolves the `target_file` path (searches `data/` recursively if path not found directly)
3. Calls the **LLM directly** (via `LlmClient`) to generate:
   - The complete modified content of `target_file`
   - The complete content of the new module
4. Writes both files to disk
5. Creates a new git branch named `fix/<bug_type>-<node_name>` (e.g., `fix/hub-exceptions-undefinedvariableintemplate`)
6. Commits both files with a message like `refactor: fix HUB in exceptions_undefinedvariableintemplate (EX04)`
7. Exports the diff to `results/fix_diff.patch`

**Why LLM-generated, not hardcoded?**  
The original hw4.0 starter hardcoded a specific refactor of `main.py` into `orchestration.py`.
That only worked for cookiecutter. `GenericFixApplier` sends the fix proposal and the actual
source code to the LLM and asks it to write both files — so it works on any Python codebase.

**Structured output format:** The LLM is instructed to use delimiters:

```
===MODIFIED_FILE===
<complete new content of target_file>
===NEW_MODULE===
<complete content of new_module_name>
```

If the delimiters are missing, `_parse_response()` raises `ValueError` immediately.

---

## Stage 4 — VerifyService: Prove the Fix Works

**Code:** `sdk.verify()` → `VerifyService.run()`  
**Input:** Modified source, `artifacts/graph.json` (before), runs pytest  
**Output:** `artifacts/graph_after.json`, `results/metrics_comparison.json`, `reports/verification.md`

The VerifyService independently confirms the fix quality:

1. **Re-runs Grphify** on the modified codebase → produces `graph_after.json`
2. **Loads both graphs** and computes metrics (hub count, SPOF count, bridge count)
3. **Compares before vs after** → saves `results/metrics_comparison.json`
4. **Runs pytest** with coverage (`uv run pytest tests/unit -q --cov=src`)
5. **Runs ruff** (`uv run ruff check src tests`) to verify no lint errors
6. **Writes `reports/verification.md`** — a human-readable summary

**Note on `metrics_improved`:** During Stage 2 (Quality Gate), `metrics_improved` is
estimated from `estimated_degree_reduction` because the fix hasn't been applied yet.
In Stage 4, `VerifyService` computes actual before/after hub counts from real graph scans.
These may differ slightly from the estimate — both are saved in their respective JSON files.

---

## Data Flow Table

| Stage | Consumes | Produces |
|-------|----------|----------|
| 1 Grphify | `data/cookiecutter/cookiecutter/*.py` | `artifacts/graph.json` · `artifacts/graph.html` · `obsidian/hot.md` · `obsidian/index.md` |
| 2 Agents | `artifacts/graph.json` · `obsidian/hot.md` · `obsidian/index.md` | `results/v2_graph_summary.json` · `results/v2_bugs.json` · `results/v2_fix_proposal.json` · `results/v2_verification.json` |
| 3 Fix Applier | `results/v2_fix_proposal.json` · target `.py` file | Modified source file · new module `.py` · `results/fix_diff.patch` · git branch + commit |
| 4 Verify | Modified source · `artifacts/graph.json` | `artifacts/graph_after.json` · `results/metrics_comparison.json` · `reports/verification.md` |

---

## ApiGatekeeper: Wrapping Every External Call

**Code:** `src/hw4/shared/gatekeeper.py` — `ApiGatekeeper`

Every call that hits an external service — the LLM, subprocess (git, pytest, ruff),
and `crew.kickoff()` — goes through `ApiGatekeeper.execute()`. This provides:

| Feature | How it works |
|---------|-------------|
| **Rate limiting** | Tracks call timestamps; waits if `requests_per_minute` is reached |
| **Retry on failure** | Re-tries up to `max_retries` times with `retry_after_seconds` delay |
| **Logging** | Every call is logged with attempt number and result |

Rate limits are configured per provider in `config/rate_limits.json` — never hardcoded:

```json
"gemini": {
  "requests_per_minute": 15,
  "max_retries": 3,
  "retry_after_seconds": 30
}
```

`HW4SDK._build_gatekeeper()` reads the active provider from the environment
(`LLM_PROVIDER`) and builds the `ApiGatekeeper` with the matching limits.

---

## Token Efficiency: Why Graph-First Matters

| Approach | Tokens needed |
|----------|--------------|
| Naive: send all 18 source files to LLM | ~23,537 |
| Graph-guided: send only graph.json + hot.md | ~645 |
| **Savings** | **97.3%** |

The graph tells agents **where to look** before they look. The Architect Detective can
identify the top hub from a 645-token graph summary instead of reading 23,537 tokens of
Python code — and it finds the same answer because the graph already encodes every
dependency relationship.

See `results/token_stats.json` and `notebooks/analysis.ipynb` for the full cost breakdown.

---

## File Map

```
src/hw4/
├── sdk/sdk.py                    ← Public entry point (HW4SDK)
├── crewai_agents/agents.py       ← 4 agent definitions
├── crewai_tasks/tasks.py         ← 4 task definitions with context= chains
├── crewai_tools/tools.py         ← 4 @tool functions
├── services/
│   ├── crew_runner_v2.py         ← Retry loop, crew orchestration
│   ├── generic_fix_applier.py    ← LLM-driven code rewrite + git commit
│   ├── graph_builder.py          ← Grphify wrapper
│   └── verify_service.py         ← Pytest + ruff + graph rescan
└── shared/
    ├── gatekeeper.py             ← Rate limiting + retry wrapper
    ├── config.py                 ← Reads config/ JSON files, validates version
    ├── git_ops.py                ← Git helpers (branch, commit, diff export)
    ├── llm_client.py             ← Direct LLM completion (for GenericFixApplier)
    ├── provider.py               ← Reads LLM_PROVIDER env var, returns model config
    └── version.py                ← VERSION = "1.00"
```
