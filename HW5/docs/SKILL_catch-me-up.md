# `/catch-me-up` — Project Onboarding Skill

## What it is

`/catch-me-up` is a Claude Code slash command (skill) that produces a complete, self-contained briefing of this project by reading the actual source files, configs, docs, and git history at invocation time. It is designed for:

- A **developer** joining the project mid-stream who needs context fast
- A **new AI agent** (Claude, GPT, Gemini, etc.) being assigned to continue this work
- A **grader or reviewer** who wants to understand the full pipeline without reading every file manually
- **Yourself** returning after a break and needing to recall where things stand

The skill reads files dynamically — it never relies on cached or training-time knowledge. Every claim in its output is sourced from a file read in that session.

---

## How to invoke it

Open a terminal in the repo root (`AI-Agents-course/`) and type:

```
/catch-me-up
```

That's it. The skill takes no arguments. It auto-detects the active homework project (HW5 if that directory exists) and produces the full briefing.

---

## What the output covers

The skill always produces these twelve sections in order:

| # | Section | What it answers |
|---|---------|-----------------|
| 1 | **Project overview** | What HW5 is, the 12-cell matrix, the research question |
| 2 | **Annotated directory tree** | What every folder and file is for |
| 3 | **Architecture — layers and contracts** | shared → services → sdk → CLI, with each class explained |
| 4 | **Full pipeline — step by step** | What happens from `uv run hw5 --mode full` to final report |
| 5 | **Every source file** | Path, classes/functions, role, line count |
| 6 | **Configuration reference** | Every key in `setup.json` and `models.json` |
| 7 | **Key design decisions** | Why the 150-line rule, ApiGatekeeper, plot_io split, etc. |
| 8 | **Test suite** | Count, coverage %, what each test file covers, skipped tests |
| 9 | **Recent changes** | Last 10 commits cross-referenced with CHANGELOG.md |
| 10 | **How to run** | Full install + all CLI modes + make targets |
| 11 | **Open tasks** | Every `[ ]` item still in TODO.md, grouped by phase |
| 12 | **For the next AI agent** | Branch, invariants, files safe to edit, where to find the PRD |

---

## When to use it

Use `/catch-me-up` at the **start** of any session where:

- You do not have the prior conversation context (new chat window, context compacted, different model)
- You are handing the project to a different agent or collaborator
- You want to verify that the project state matches what you expect before making changes
- You are generating a PR description or submission summary and want ground-truth project state

Do **not** use it when:
- You are mid-task and already have full context — it is expensive (reads many files)
- You only need one specific file — use `Read` directly instead
- You need live pipeline metrics — run `uv run pytest` and `uv run ruff check` directly

---

## For AI agents reading this file

If you are an AI agent that has been assigned to work on this project, follow these steps before touching any code:

1. **Run `/catch-me-up`** to get a complete picture of the current state.
2. Read `docs/PRD.md` for acceptance criteria.
3. Read `docs/TODO.md` — tasks marked `[ ]` are open; tasks marked `[x]` are done.
4. Read `docs/PLAN.md` for the phase-by-phase implementation strategy.

### Invariants you must never break

| Invariant | Why |
|-----------|-----|
| Every `src/hw5/` Python file must be ≤ 150 lines | Enforced by `make lint` via `awk`. The Makefile will fail CI if violated. |
| Every LLM call must go through `ApiGatekeeper.execute()` | Prevents rate-limit errors; required by the shared gatekeeper contract in `PRD.md`. |
| `cell_id` format is always `{model}__{framework}__{quant}` | Double underscore. Splitting on `"__"` must always yield exactly 3 parts. |
| `uv` manages all dependencies — never use `pip install` | `uv.lock` is committed; `pip` would create a divergent environment. |
| `QuantizationConfig` only accepts bits ∈ {2, 4, 8} | `from_label("Q16")` raises `ValueError`. Do not add new quant levels without updating the validator. |
| Tests must stay ≥ 85% coverage | `pyproject.toml` sets `fail_under = 85`. New code needs tests. |

### Architecture in one paragraph

`EvalPipelineSDK` is the single entry point. It owns a `ModelRegistry` (loaded from `config/models.json`), an `ApiGatekeeper` (rate limiter), and an `EvaluationLoop` (builds the 12-cell matrix). Each cell runs through a `RunnerFactory` → either `AirLLMRunner` (layer-streaming) or `OllamaRunner` (local server). A `SystemMonitor` daemon thread samples CPU/RAM/swap/VRAM while inference runs. Results are saved as JSON by `CellPersistence`, then visualized by `Plotter` + `plot_io`, summarized by `SummaryGenerator`, and assembled into an HTML report by `ReportWriter`. The `shared/` layer (Config, QuantizationConfig, ApiGatekeeper, constants) is imported by all other layers but depends on nothing inside `hw5/`.

### Key files to read first

```
HW5/src/hw5/sdk/sdk.py          ← the single facade; understand this first
HW5/src/hw5/services/eval_loop.py  ← builds and runs the 12-cell matrix
HW5/src/hw5/shared/config.py    ← all runtime knobs
HW5/config/setup.json           ← active runtime configuration
HW5/config/models.json          ← which models and quant levels are evaluated
HW5/docs/TODO.md               ← what is done and what remains
```

### Current project state (as of last update)

- **Branch**: `nagham-hw5`
- **Phases complete**: 1–10 (all implementation, docs, and submission tasks)
- **Tests**: 270 passed, 7 skipped (hardware-dependent: CUDA, Ollama server, AirLLM import)
- **Coverage**: 92.51% (threshold: 85%)
- **Ruff violations**: 0
- **Source files over 150 lines**: 0
- **Last structural change**: `plot_io.py` extracted from `plotter.py` to keep both files under the 150-line limit; `results_to_df()` and `plot_tradeoff_scatter()` live in `plot_io.py`

---

## Skill file location

The skill is defined at:

```
AI-Agents-course/.claude/commands/catch-me-up.md
```

This is a Claude Code project-level command. Any Claude Code session opened at the `AI-Agents-course/` repo root can invoke it with `/catch-me-up`.
