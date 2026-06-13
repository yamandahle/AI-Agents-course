# PRD: Grade Fixes — Submission Quality Hardening

**Status:** In Progress  
**Priority:** P0 — required for ≥90 score  
**Created:** 2026-06-13

---

## Problem Statement

Four gaps currently limit the project score to ~78–83:

| Gap | Current | Required | Impact |
|---|---|---|---|
| Python-generated graph missing from PDF | script exists, never run | in PDF via `\includegraphics` | −10 pts |
| Ruff lint violations | 34 errors | 0 | −5 to −10 pts |
| Test suite failures + low coverage | 13 failing, 24.49% | 0 failing, ≥85% | −10 to −15 pts |
| No Jupyter notebook | `notebooks/` empty | results analysis notebook | −3 pts |

---

## Fix 1 — Python Graph in PDF

### Background
The assignment requires "לפחות גרף אחד שנוצר בקוד Python" (at least one graph created with Python code).
`assets/graphs/generate_graph.py` exists and produces `accuracy_curve.pdf` via matplotlib.
The draft has never included this graph.

### Requirements
- R1.1 Run `generate_graph.py` with meaningful axis labels matching the article's content
- R1.2 Save output to `assets/graphs/accuracy_curve.pdf`
- R1.3 Wire `\includegraphics[width=\textwidth]{../assets/graphs/accuracy_curve.pdf}` into `draft_final.tex` inside a `\begin{figure}[H]` with a descriptive caption and `\label`
- R1.4 Recompile `draft_final.tex` → `article_final.pdf` and verify the graph appears

### Success Criteria
- `assets/graphs/accuracy_curve.pdf` exists with a two-series line chart
- `article_final.pdf` contains a clearly labelled Python-generated figure
- `\caption` text matches the prose paragraph above the figure

---

## Fix 2 — Ruff Zero Violations

### Background
`uv run ruff check src/` reports 34 errors. The submission guidelines require zero violations.

### Root Causes (by file)

| File | Violations | Types |
|---|---|---|
| `latex/latex_compiler.py` lines 21–50 | 27× E501 + 2× F601 + 1× B005 | Long lines in `_KNOWN_DOMAIN_META` dict; duplicate key `"weforum.org"`; `.strip()` with multi-char string |
| `shared/llm_client.py:7` | 1× F401 | `Any` imported but unused |
| `tools/chart_checker.py:265` | 1× S607 | Partial executable path in `subprocess.run` |
| `writing/_draft_prompt.py:190,247,282` | 3× W605 + 1× E501 | Invalid escape `\R` in raw-string context; one long line |
| `writing/reviewer.py:132,147` | 1× F841 + 1× S110 | Unused variable; bare `except: pass` |

### Requirements
- R2.1 Wrap `_KNOWN_DOMAIN_META` values onto multiple lines (or use a multi-line string format) to fix E501
- R2.2 Remove the duplicate `"weforum.org"` key (F601) — keep the better entry
- R2.3 Replace `.strip("% ")` multi-char strip with chained `.strip("%").strip()` (B005)
- R2.4 Remove unused `Any` import from `llm_client.py` (F401)
- R2.5 Use `"lualatex"` as full path or add `# noqa: S607` in `chart_checker.py` (S607)
- R2.6 Fix `\R` escape sequences in `_draft_prompt.py` — use raw strings `r"..."` or `\\R` (W605)
- R2.7 Delete the unused `comments_match` variable in `reviewer.py` (F841)
- R2.8 Replace bare `except: pass` with `except Exception: logger.debug(...)` in `reviewer.py` (S110)
- R2.9 Run `uv run ruff check src/` → must output "All checks passed."

### Success Criteria
- `uv run ruff check src/` exits with code 0 and prints nothing or "All checks passed."

---

## Fix 3 — Tests: Zero Failures + ≥85% Coverage

### Background
- **13 failing tests**: all caused by the same bug — tests mock `gate.execute()` to return an Anthropic-style response object (`.content[0].text`) but the actual code accesses `.text` on an `LLMResponse` dataclass
- **24.49% coverage**: `latex_sanitizer.py` (384 lines, 0%) is the single biggest gap; `sdk/sdk.py` (90 lines, 0%) and `draft_generator.py` (90 lines, 0%) are next

### Requirements

**3a — Fix 13 failing tests**
- R3a.1 Update `_mock_response()` helpers in 5 test files to return `LLMResponse(text=..., input_tokens=10, output_tokens=20, model="mock", cost_usd=0.0)` instead of Anthropic-style objects
- R3a.2 Fix `test_compiler.py::test_run_pass_raises_on_nonzero_exit` — configure subprocess mock correctly
- R3a.3 Fix `test_research_tasks.py::test_make_research_batch_task_creates_task_with_human_input`
- R3a.4 `uv run pytest --no-cov -q` → 0 failures

**3b — Increase coverage to ≥85%**
Priority targets (by lines gained per effort):

| File | Current | Lines Uncovered | Strategy |
|---|---|---|---|
| `latex/latex_sanitizer.py` | 0% | 384 | Write 2 test files with full step coverage |
| `sdk/sdk.py` | 0% | 90 | Mock pipeline, test all SDK methods |
| `writing/draft_generator.py` | 0% | 90 | Fix mocks → existing tests pass; add edge cases |
| `writing/reviewer.py` | 35% | 42 | Add tests for parse paths |
| `writing/editor.py` | 32% | 34 | Add apply-review tests |
| `writing/context_loader.py` | 31% | 31 | Add loader path tests |
| `writing/few_shot_loader.py` | 22% | 32 | Add PDF mock tests |
| `writing/review_loop.py` | 28% | 26 | Add loop iteration tests |
| `latex/latex_compiler.py` | 51% | 42 | Add compile/validate path tests |
| `tools/researcher_handler.py` | 50% | 27 | Fix mock → tests pass |
| `writing/optimizer.py` | 42% | 23 | Add optimizer tests |
| `writing/loop_controller.py` | 35% | 20 | Add controller tests |

### Success Criteria
- `uv run pytest --cov=src --cov-fail-under=85 -q` exits 0
- 0 test failures

---

## Fix 4 — Jupyter Notebook for Results Analysis

### Background
Section 9 of the submission guidelines requires "מחברת ניתוח תוצאות" (results analysis notebook). `notebooks/` is empty.

### Requirements
- R4.1 Create `notebooks/results_analysis.ipynb`
- R4.2 Load `results/metrics.jsonl` — parse latency, tokens, cost per step
- R4.3 Plot bar chart: latency per pipeline step (matplotlib)
- R4.4 Plot bar chart: token usage (input vs output) per step
- R4.5 Print total cost estimate and summary table
- R4.6 All cells must be runnable without API keys (reads from existing file)

### Success Criteria
- `notebooks/results_analysis.ipynb` exists with ≥10 cells
- All cells execute without error when `metrics.jsonl` is present
- At least 2 matplotlib charts visible in the notebook output
