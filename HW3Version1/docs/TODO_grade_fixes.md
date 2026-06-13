# TODO: Grade Fixes

Legend: [ ] = pending, [x] = done

---

## Phase 1 — Ruff Zero Violations

- [ ] R1. `latex_compiler.py` — wrap `_KNOWN_DOMAIN_META` values onto multiple lines (fix 27× E501)
- [ ] R2. `latex_compiler.py` — remove duplicate `"weforum.org"` key (fix 2× F601)
- [ ] R3. `latex_compiler.py` — replace `.strip("% ")` with `.strip("%").strip()` (fix B005)
- [ ] R4. `llm_client.py` — remove unused `Any` import (fix F401)
- [ ] R5. `chart_checker.py:265` — add `# noqa: S607` to subprocess.run call
- [ ] R6. `_draft_prompt.py:190` — fix `\R` invalid escape in string literal (fix W605)
- [ ] R7. `_draft_prompt.py:247` — fix `\R` invalid escape (fix W605)
- [ ] R8. `_draft_prompt.py:282` — fix `\R` invalid escape + break E501 line (fix W605 + E501)
- [ ] R9. `reviewer.py:132` — delete unused `comments_match` variable (fix F841)
- [ ] R10. `reviewer.py:147` — replace `except: pass` with `except Exception: logger.debug(...)` (fix S110)
- [ ] R11. Run `uv run ruff check src/` → verify "All checks passed."

---

## Phase 2 — Fix 13 Failing Tests

- [ ] T1. `test_draft_generator.py` — update `_mock_response()` to return `LLMResponse` dataclass
- [ ] T2. `test_content_filter.py` — update `_mock_anthropic_response()` to return `LLMResponse`
- [ ] T3. `test_citation_extractor.py` — update mock helper to return `LLMResponse`
- [ ] T4. `test_researcher_handler.py` — update mock helper to return `LLMResponse`
- [ ] T5. `test_llm_client.py::test_google_provider_complete` — fix Google provider mock
- [ ] T6. `test_compiler.py::test_run_pass_raises_on_nonzero_exit` — fix subprocess mock
- [ ] T7. `test_research_tasks.py::test_make_research_batch_task` — fix CrewAI task assertion
- [ ] T8. `tests/integration/test_context_pipeline.py` — fix mock chain for integration test
- [ ] T9. Run `uv run pytest --no-cov -q` → verify 0 failures, 192 passed

---

## Phase 3 — Python Graph in PDF

- [ ] G1. Run `uv run python assets/graphs/generate_graph.py --title "AI Diagnostic Accuracy vs. Training Epochs" --xlabel "Training Epoch" --ylabel "Diagnostic Accuracy (%)" --output assets/graphs/accuracy_curve.pdf`
- [ ] G2. Verify `assets/graphs/accuracy_curve.pdf` exists and is non-empty
- [ ] G3. Insert `\begin{figure}[H]...\includegraphics...\end{figure}` block into `draft_final.tex` in the AI Performance Metrics section
- [ ] G4. Add descriptive `\caption` that references the Python script and matches prose
- [ ] G5. Add `\label{fig:accuracy_curve}` to the figure
- [ ] G6. Recompile: `lualatex --interaction=nonstopmode --halt-on-error draft_final.tex` in results/
- [ ] G7. Run biber + 2nd lualatex pass to update references
- [ ] G8. Verify `article_final.pdf` contains the accuracy curve figure

---

## Phase 4a — `latex_sanitizer.py` Coverage (384 lines → ≥85%)

- [ ] S1. Create `tests/unit/test_latex/test_sanitizer_steps.py` (≤150 lines)
- [ ] S2. Test `_fix_malformed_envs()` pattern 0a: `\end{env>` → `\end{env}`
- [ ] S3. Test pattern 0b: `</tabular>` HTML-style tag → `\end{tabular}`
- [ ] S4. Test pattern 0c: `</tabular}` mixed → `\end{tabular}`
- [ ] S5. Test pattern 0d: `\begin{tabularx}...\end{tabular}` mismatch → `\end{tabularx}`
- [ ] S6. Test pattern 0e: unclosed `\begin{axis}` before `\end{tikzpicture}` → inject `\end{axis}`
- [ ] S7. Test pattern 0f: bare `&` in `\node{A & B}` → `\node{A \& B}`
- [ ] S8. Test `_fix_missing_ragged2e()`: `ragged2ce` typo normalised → `ragged2e`
- [ ] S9. Test `_fix_missing_ragged2e()`: deduplication of multiple `\usepackage{ragged2e}`
- [ ] S10. Create `tests/unit/test_latex/test_sanitizer_full.py` (≤150 lines)
- [ ] S11. Test `_fix_table_alignment()`: `\begin{tabular}{ll}` → `\begin{tabularx}{\textwidth}`
- [ ] S12. Test `_fix_table_alignment()` body-only: titlepage `{rl}` table untouched
- [ ] S13. Test `_fix_arrow_labels()`: adds `fill=white` to `\draw[->]` edge node missing it
- [ ] S14. Test `_fix_invalid_cite_keys()`: `\cite{keragon.com}` remapped to curated key
- [ ] S15. Test `_fix_invalid_cite_keys()`: valid curated key unchanged
- [ ] S16. Test `_fix_invalid_cite_keys()`: multi-key `\cite{a,b}` where `b` is invalid
- [ ] S17. Test `sanitize()` end-to-end: full LaTeX string with multiple issues → clean output
- [ ] S18. Test `validate()`: valid document with no warnings → empty list
- [ ] S19. Test `_is_root_domain_url()`: `https://www.example.com` → True; `https://www.example.com/article/123` → False

---

## Phase 4b — `sdk/sdk.py` Coverage (90 lines → ≥80%)

- [ ] SD1. Create `tests/unit/test_sdk/` directory and `__init__.py`
- [ ] SD2. Create `tests/unit/test_sdk/test_sdk.py` (≤150 lines)
- [ ] SD3. Test SDK init with mocked config
- [ ] SD4. Test `run_research()` method with mocked ResearcherAgent
- [ ] SD5. Test `run_writing()` method with mocked WriterAgent
- [ ] SD6. Test `run_full_pipeline()` with mocked agents

---

## Phase 4c — Writing Module Coverage

- [ ] W1. `test_reviewer.py` — add test for JSON parse success path (mock LLM returning valid JSON)
- [ ] W2. `test_reviewer.py` — add test for fallback ArticleReview on bad JSON
- [ ] W3. `test_editor.py` — add test for `apply_reviews()` with mocked LLM
- [ ] W4. `test_editor.py` — add test for empty review list (no-op path)
- [ ] W5. `test_context_loader.py` — add test for `load()` with tmp_path files
- [ ] W6. `test_context_loader.py` — add test for missing guideline file
- [ ] W7. `test_few_shot_loader.py` — add test with mocked `fitz.open()` returning pages
- [ ] W8. `test_few_shot_loader.py` — add test for empty PDF directory
- [ ] W9. `test_review_loop.py` — add test for single loop iteration with mocked reviewer+editor
- [ ] W10. `test_review_loop.py` — add test for early exit when score_threshold met
- [ ] W11. `test_optimizer.py` (create if missing) — add tests for optimizer pass
- [ ] W12. `test_loop_controller.py` (create if missing) — add tests for controller logic
- [ ] W13. `test_evaluator.py` — add tests for uncovered evaluator branches

---

## Phase 4d — Tools + Compiler Coverage

- [ ] TC1. `test_citation_extractor.py` — add test for URL detection path (after fixing mock)
- [ ] TC2. `test_citation_extractor.py` — add test for plain-text detection path
- [ ] TC3. `test_researcher_handler.py` — add test for batch count increment (after fixing mock)
- [ ] TC4. `test_compiler.py` — add test for `validate()` with `.log` containing "undefined" warning
- [ ] TC5. `test_compiler.py` — add test for `_repair_missing_citations()` stub generation
- [ ] TC6. Run `uv run pytest --cov=src --cov-report=term-missing -q` → check coverage

---

## Phase 5 — Jupyter Notebook

- [ ] N1. Create `notebooks/results_analysis.ipynb` with nbformat structure
- [ ] N2. Cell 1 (markdown): title "Pipeline Results Analysis"
- [ ] N3. Cell 2 (code): imports — pandas, matplotlib, json, pathlib
- [ ] N4. Cell 3 (code): load `results/metrics.jsonl` → DataFrame
- [ ] N5. Cell 4 (code): display `.head()` and column info
- [ ] N6. Cell 5 (code): group by `step`, compute mean `latency_ms`
- [ ] N7. Cell 6 (code): bar chart — mean latency per pipeline step
- [ ] N8. Cell 7 (code): group by `step`, sum `input_tokens` and `output_tokens`
- [ ] N9. Cell 8 (code): stacked bar chart — tokens per step (input vs output)
- [ ] N10. Cell 9 (code): total cost in USD — `metrics['cost_usd'].sum()`
- [ ] N11. Cell 10 (markdown): summary + interpretation paragraph

---

## Final Verification

- [ ] V1. `uv run ruff check src/` → exit code 0, "All checks passed."
- [ ] V2. `uv run pytest --no-cov -q` → 0 failures
- [ ] V3. `uv run pytest --cov=src --cov-fail-under=85 -q` → PASSED
- [ ] V4. `ls assets/graphs/accuracy_curve.pdf` → exists
- [ ] V5. `grep "accuracy_curve" results/draft_final.tex` → found
- [ ] V6. `ls notebooks/results_analysis.ipynb` → exists
- [ ] V7. Open `results/article_final.pdf` → Python graph visible
