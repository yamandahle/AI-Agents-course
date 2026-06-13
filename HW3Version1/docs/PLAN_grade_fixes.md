# Plan: Grade Fixes Execution

**Estimated time:** 3–4 hours  
**Order:** Fix 2 (ruff) → Fix 3a (test failures) → Fix 1 (graph) → Fix 3b (coverage) → Fix 4 (notebook)

Ruff and test-failure fixes are pre-conditions for coverage measurement. Graph fix is isolated. Coverage is the longest phase.

---

## Phase 1 — Ruff Zero Violations (30 min)

**File: `latex/latex_compiler.py`**
- Wrap `_KNOWN_DOMAIN_META` tuple values as multi-line with `(  )` continuation
- Remove duplicate `"weforum.org"` key — keep the entry with more fields
- Replace `.strip("% ")` with `.strip("%").strip()`

**File: `shared/llm_client.py`**
- Remove `Any` from the `typing` import line

**File: `tools/chart_checker.py`**
- Add `# noqa: S607` to the `subprocess.run` call, or use `shutil.which("lualatex")`

**File: `writing/_draft_prompt.py`**
- Wrap the 3 `\R` occurrences: change `"\R"` → `r"\R"` or `"\\R"` in f-string contexts
- Break the one E501 line at a logical boundary

**File: `writing/reviewer.py`**
- Delete `comments_match` variable
- Change `except: pass` → `except Exception: logger.debug("JSON parse fallback", exc_info=True)`

**Verify:** `uv run ruff check src/` → "All checks passed."

---

## Phase 2 — Fix 13 Failing Tests (45 min)

**Root cause:** Mocks return Anthropic-format response (`.content[0].text`) but code reads `LLMResponse.text`.

**Pattern fix — apply to 5 test files:**
```python
# OLD (wrong)
def _mock_response(text):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg

# NEW (correct)
from article_writer.shared.llm_client import LLMResponse
def _mock_response(text):
    return LLMResponse(text=text, input_tokens=10, output_tokens=20, model="mock", cost_usd=0.0)
```

**Files to update:**
1. `tests/unit/test_writing/test_draft_generator.py` — `_mock_response()`
2. `tests/unit/test_tools/test_content_filter.py` — `_mock_anthropic_response()`
3. `tests/unit/test_tools/test_citation_extractor.py` — `_mock_llm_response()`
4. `tests/unit/test_tools/test_researcher_handler.py` — `_mock_llm_response()`
5. `tests/unit/test_shared/test_llm_client.py` — Google provider mock

**Additional fixes:**
- `test_compiler.py::test_run_pass_raises_on_nonzero_exit` — fix subprocess mock
- `test_research_tasks.py::test_make_research_batch_task` — fix CrewAI task mock

**Verify:** `uv run pytest --no-cov -q` → 0 failures

---

## Phase 3 — Python Graph in PDF (30 min)

1. Run: `uv run python assets/graphs/generate_graph.py --title "AI Model Accuracy vs. Training Epochs" --xlabel "Training Epoch" --ylabel "Diagnostic Accuracy" --output assets/graphs/accuracy_curve.pdf`
2. Verify `accuracy_curve.pdf` exists
3. Insert into `results/draft_final.tex` — find the AI Performance section (around Figure 1) and add a new `\begin{figure}[H]` block referencing the graph
4. Recompile: `cd results && lualatex --interaction=nonstopmode draft_final.tex` × 2 passes
5. Verify graph appears in `article_final.pdf`

---

## Phase 4 — Coverage to ≥85% (2 hours)

**Target: cover ~1350 additional lines from current 547 covered.**

**Step 4a — `latex_sanitizer.py` (384 lines, 0%) — highest priority**
Write `tests/unit/test_latex/test_sanitizer_steps.py` and `test_sanitizer_full.py`:
- Test each of the 12 `sanitize()` steps with crafted LaTeX strings that trigger them
- Test `_fix_malformed_envs()` sub-patterns 0a–0f individually
- Test `_fix_invalid_cite_keys()` with known bad keys and verify remapping
- Test `_fix_arrow_labels()` with TikZ draw lines missing `fill=`
- Test `validate()` with root-domain URLs and missing files
Expected coverage gain: ~320 lines

**Step 4b — `sdk/sdk.py` (90 lines, 0%)**
Write `tests/unit/test_sdk/test_sdk.py`:
- Mock the full pipeline (ResearcherAgent, WriterAgent, DraftGenerator, ReviewLoop)
- Test each public SDK method

**Step 4c — Writing module coverage (reviewer, editor, context_loader, etc.)**
- `test_reviewer.py` — add tests for Pydantic parse path, fallback path
- `test_editor.py` — add apply-review tests with mocked LLM
- `test_context_loader.py` — add loader with tmp_path fixtures
- `test_few_shot_loader.py` — add PDF mock (mock `fitz.open`)
- `test_review_loop.py` — add loop iteration mock

**Step 4d — Tools coverage (now that mocks are fixed)**
Re-run failing tool tests. Check if additional test cases needed for uncovered branches.

**Verify:** `uv run pytest --cov=src --cov-report=term-missing -q` → ≥85%

---

## Phase 5 — Jupyter Notebook (30 min)

Create `notebooks/results_analysis.ipynb` with cells:
1. Title + description markdown
2. Import pandas, matplotlib, json, pathlib
3. Load `results/metrics.jsonl` into DataFrame
4. Show first 5 rows + column info
5. Group by step, compute mean latency
6. Bar chart: mean latency per step
7. Group by step, sum tokens
8. Stacked bar chart: input vs output tokens per step
9. Compute total cost
10. Summary markdown table

---

## Verification Checklist

```bash
uv run ruff check src/                              # "All checks passed."
uv run pytest --no-cov -q                           # 0 failures
uv run pytest --cov=src --cov-fail-under=85 -q      # PASSED
ls assets/graphs/accuracy_curve.pdf                 # exists
grep "accuracy_curve" results/draft_final.tex       # found
ls notebooks/results_analysis.ipynb                 # exists
```
