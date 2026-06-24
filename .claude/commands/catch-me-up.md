You are catching someone up on this project from scratch. Your job is to produce a thorough, structured briefing so that whoever reads your output — a developer, a new AI agent, or a grader — needs zero other context to understand the project.

Read the actual files. Do not rely on memory or training data. Every claim must come from a file you read in this session.

---

## Steps to follow

1. Detect which homework project is active by checking which directories exist:
   - `HW5/` → AirLLM vs Ollama evaluation pipeline
   - `HW4version2/` → Graph-based bug analysis pipeline
   Run: `ls` in the repo root to confirm.

2. For HW5 (primary project), read these files in order:
   - `HW5/docs/PRD.md` — requirements and acceptance criteria
   - `HW5/docs/PLAN.md` — phase-by-phase implementation plan
   - `HW5/docs/TODO.md` — task status (count `[x]` vs `[ ]`)
   - `HW5/README.md` — user-facing documentation
   - `HW5/config/setup.json` — runtime config
   - `HW5/config/models.json` — model registry (what models, what quantizations)
   - Every `.py` file under `HW5/src/hw5/` — the full source
   - `HW5/pyproject.toml` — dependencies, ruff/pytest config
   - `HW5/Makefile` — available make targets
   - `HW5/prompts_ive_used.md` — prompting history
   - `HW5/CHANGELOG.md` — version history of changes

3. Run the following commands and include their output verbatim:
   ```
   cd HW5 && find src -name "*.py" | sort
   cd HW5 && uv run ruff check src/ 2>&1
   cd HW5 && uv run pytest tests/ -q --tb=no 2>&1 | tail -10
   cd HW5 && find src -name "*.py" -exec awk 'END{print NR"\t"FILENAME}' {} \; | sort -n | tail -10
   git log --oneline -10
   ```

---

## Summary format — produce ALL sections

### 1. Project overview (one paragraph)
What is HW5, what research question does it answer, what is the 12-cell evaluation matrix (2 models × 2 frameworks × 3 quants), and what is the assignment context.

### 2. Annotated directory tree
Print every top-level folder and file under `HW5/`. After each item, add one line: what lives there and why it exists.

### 3. Architecture — layers and contracts
Describe the four layers:
- **shared/** — Config, QuantizationConfig, ApiGatekeeper, constants
- **services/** — AirLLMRunner, OllamaRunner, SystemMonitor, MetricsBuffer, Plotter, plot_io, SummaryGenerator, ReportWriter, EvalLoop, ModelRegistry, CellPersistence
- **sdk/** — EvalPipelineSDK (the single facade used by callers)
- **main.py** — CLI entry point

For each class, state: what it does, what it takes as input, what it returns, and which other classes it depends on.

### 4. Full pipeline — step by step
Walk through exactly what happens when `uv run hw5 --mode full` is invoked:
1. CLI parsing → EvalPipelineSDK instantiation
2. ModelRegistry loads `config/models.json` and validates hook placeholders
3. EvaluationLoop builds the 12-cell matrix (model × framework × quant)
4. For each cell:
   a. RunnerFactory selects AirLLMRunner or OllamaRunner
   b. Runner.load() downloads/initialises model
   c. SystemMonitor.start() begins daemon sampling thread
   d. Runner.infer() generates tokens, ApiGatekeeper rate-limits
   e. SystemMonitor.stop() returns MetricsSnapshot
   f. CellPersistence.save_result() writes JSON to results/
5. Plotter generates 4 charts (heatmap, RAM timeline, VRAM bar, tradeoff scatter)
6. plot_io.save_all() writes 8 files (PNG + SVG × 4)
7. SummaryGenerator.generate_all() builds statistics tables
8. ReportWriter.to_html() assembles final report

### 5. Every source file — role and contents
For each file under `HW5/src/hw5/`, list:
- Path
- Classes / functions defined
- Role in the pipeline
- Line count (must be ≤ 150)

### 6. Configuration reference
For every key in `config/setup.json` and `config/models.json`, explain what it controls and what happens if it is changed.

### 7. Key design decisions and constraints
Explain **why** each of these choices was made — read the PRD and PLAN for the rationale:
- 150-line hard limit on every `src/` file
- ApiGatekeeper wraps every LLM call (token-bucket rate limiting)
- plot_io.py extracted from plotter.py (separation of I/O from rendering)
- `results_to_df()` and `plot_tradeoff_scatter()` moved to plot_io.py
- MetricsBuffer uses threading.Lock (thread-safe sampling)
- VRAMSpikeEvent uses `is_significant(threshold_mb)` for spike detection
- `cell_id` format: `{model}__{framework}__{quant}` (double underscore)
- `from_label("Q16")` raises ValueError (only Q2/Q4/Q8 are valid)
- ModelRegistry raises RegistryError on `<HOOK` placeholder found
- AirLLMRunner uses `to_airllm_param()` to map quant → compression string

### 8. Test suite — coverage and structure
- How many tests total, how many pass, how many skipped
- Coverage percentage and threshold
- What each test file covers (unit vs integration)
- What the 7 skipped tests are skipping and why
- Current ruff violation count

### 9. Recent changes (last 10 commits)
For each commit, explain what changed and why. Read `git log --oneline -10` and cross-reference with `HW5/CHANGELOG.md`.

### 10. How to run — complete instructions
```bash
# Install dependencies
cd HW5 && uv sync

# Run full evaluation (all 12 cells)
uv run hw5 --mode full

# Run a single cell
uv run hw5 --mode single --cell phi3__airllm__Q4

# Plot results from saved JSON
uv run hw5 --mode plot

# Generate HTML report
uv run hw5 --mode report

# Dry-run (list cells, no execution)
uv run hw5 --dry-run

# Run tests with coverage
uv run pytest tests/ -q

# Lint
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Full quality check
make lint test
```

### 11. Open tasks and known gaps
Read `HW5/docs/TODO.md`. List every task still marked `[ ]`. Group by phase. Note the completion percentage per phase.

### 12. For the next AI agent taking over
State explicitly:
- The branch name (`nagham-hw5`)
- What the 150-line rule means and which tool enforces it
- That ApiGatekeeper MUST wrap every LLM call
- That `cell_id` always uses double underscores
- That `uv` (not pip) manages dependencies
- Which files are safe to edit vs which are generated/locked
- Where to find acceptance criteria (PRD.md) and the implementation checklist (TODO.md)

---

Be exhaustive. Quote key code snippets when the logic is non-obvious. If a design decision would surprise a reader, explain it. The goal: whoever reads this output can immediately open any file, understand it, and continue the work.
