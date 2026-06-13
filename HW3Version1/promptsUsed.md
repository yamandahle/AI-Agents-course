# Prompts Used — HW3 Article-Writing Multi-Agent Network

---

## Prompt 1 — Architecture Stage Kick-off

> we are going to build a full project I am the manager and you are a critical worker engineer, the project is to build a network that can write an article with length 15 pages with additional restrictions you can find them in file "\\wsl.localhost\Ubuntu\home\nagham1023\AI-Agents-course\HW3Version1\main-L06-summary-and-ex03-defination.pdf" and the project should build with instructions from this file "\\wsl.localhost\Ubuntu\home\nagham1023\AI-Agents-course\HW3Version1\software_submission_guidelines-V3.pdf" we are going to divide the work into 3 stages.
>
> The first stage is we are going to define the architecture we are going to use. So we need in addition to you 2 agents:
>
> **Researcher Agent** — who is exploratory (find information through various sources) and directed by human feedback: "search, read, pivot, search again."
>
> **Writer Agent** — who is deterministic, follows tone, structure, final edits with human feedback (human review in the end only): "draft, critique, edit, format"
>
> The two agents in the same project to share context.
>
> The first agent should behave as:
> 1. Read human-written article guideline to understand the topic to research
> 2. Iteratively do web searches to learn more about the topic and gather material, following user feedback after each batch of web searches
> 3. Revise all the gathered content — do not skip any content, do not keep any untrustworthy content, keep only the most relevant.
> 4. Write all gathered content into a final artefact which will be used by the writer agent.
>
> For web searches solution use Gemini or Perplexity — get precise answers to search queries with citations. We're going to use MCP server and use MCP tools to do the API calls. This is why you need to add tools such as deep research, researcher handler — and each tool should add prompt as the query.
>
> The writing flow will have 3 phases:
> - **Phase 1:** Load the context with 2 markdown files (guidelines, research) and another 2 files (profiles/ and few-shot examples).
> - **Phase 2:** Generate the initial draft.
> - **Phase 3:** Improve the post with evaluator-optimizer loop.
>
> The guideline is "what to write" — contains things like the Topic, angle, key points, and narrative arc — these in the .md file with the research.md file with LLM prompt will give us the draft.
>
> The writing profiles are the "how to write it" — will be static and configured and contains 3 Markdown files: Structure, Terminology, Characters — and these 3 will be injected into every prompt. So profiles with few-shot examples will go into the writer prompt that produces the draft.
>
> Prepare the PRD file and the PLAN file for what I explained and make a TODO file with 800 todos in the list and add this prompt to markdown file with name promptsUsed.

### Key Decisions

| Decision | Detail |
|---|---|
| Framework | CrewAI (agent orchestration) |
| Search API | Gemini or Perplexity via MCP server |
| Context sharing | Both agents in the same CrewAI Crew, context passed via Task context chain |
| Researcher feedback | Human-in-the-loop after each search batch |
| Writer feedback | Human review at the end only |
| Writing phases | 3: Context Load → Draft Generation → Evaluator-Optimizer Loop |
| Writing profiles | Static MD files: Structure.md, Terminology.md, Characters.md |
| Few-shot examples | Injected into every writer prompt alongside profiles |
| Output format | LaTeX → PDF (LuaLaTeX / MiKTeX) |
| Article length | ~15 pages |

---

## Prompt 2 — Stage 3 Extension

> I updated the few-shot-examples with real pdf examples as they should so modify the project to adapt to this change. add the ability to change the model we use from configuration we work me and my partner she will use sonnet and ill use gemini model so make sure the .env example is adapting to this and the guideline you write it according to the few-shot-examples and add a README file for this project contains how to run it the directories and a full summary of how it works. now for the evaluation phase I need a 3-4 loops between the writer and reviewer and make sure they keep each version in a file with the version name in the results file and final will have final version and also in the results file and make sure the 2 agents has separate context the review only can read the draft not the writer context!, how the review works, the input will be the current post and context: guideline+research+profiles(to check against) the output is review pydantic object the review model contains(profile(which constraint), location(where in the article), comment(what is wrong ~1-2 lines), and then the next step is applying the correctness which is how the edit works, the input: current post+ structured reviews, the context: guidlines+ research+ profiles+ few-shot- examples(same as the initial writer) the priority: guideline>research> profile violations, make a file and store all the traces every LLM/tool call with full I/O +metadata, make a file and save the latency and cost per-step timing, tokens,dollars. now let us build an eval dataset from scratch, extract 20 real articles with ~13-20 pages from MDPI do a reverse-Engineer(guidlines + research are the input) and generate this will be the output label the outputs with binary pass/fail + 3 sentence critique) then split it into train/dev/test then build the evaluator and then evaluate the evaluator! so repeat until converge (measure F1= precision * recall) Run the LLM judge on dev split compute F1 score adjust LLM judge prompt/examples and for final validation run on test split for final validation. make prd and plan files and then a todo list with 650 todos on the list, add this prompt to the used prompts file and execute the todo list

### Key Decisions

| Decision | Detail |
|---|---|
| Few-shot format | Changed from `.md` to real MDPI PDFs (PyMuPDF/fitz extraction) |
| LLM provider switching | `LLM_PROVIDER` env var — `anthropic` (partner) or `google` (Nagham) |
| Reviewer context isolation | Reviewer sees ONLY draft + guideline + research + profiles — never few-shots |
| Review output type | `ArticleReview` Pydantic model with list of `ReviewComment(profile, location, comment)` |
| Editor priority | guideline violations > research violations > profile violations |
| Version tracking | `draft_v1.tex`, `review_v1.json`, ..., `draft_final.tex` in `results/` |
| Tracing | `traces.jsonl` — full I/O + metadata per LLM/tool call |
| Metrics | `metrics.jsonl` — latency_ms, tokens, cost_usd per step |
| Eval dataset | 20 MDPI articles (13–20 pages), labelled PASS/FAIL + 3-sentence critique |
| Eval splits | train/dev/test split saved as JSONL |
| Judge convergence | F1 on dev split; refine prompt until F1 ≥ 0.80 |
| Final eval | Run winning judge on test split (held-out throughout refinement) |

---

## Prompt 3 — Content Quality PRD: LaTeX Sanitizer + Citation Hardening

> do a PRD and a plan and execute it:
>
> **A. LaTeX document quality (11 items)**
> — clean `references.bib` to 30 curated keys only (no root-domain URLs, full academic metadata on every entry)
> — add `\usepackage{ragged2e}` and update all tables to `tabularx{\textwidth}` with `>{\RaggedRight\arraybackslash}X` columns
> — add a Verification Constraint hard-rule to the draft prompt: LLM must write a comment in a `<!-- VERIFY -->` block after every claim it cannot cite
> — add a Structural Code Alignment hard-rule: every label, axis tick, and chart title must match the exact wording used in the prose paragraph that references the figure
> — add a LaTeX Layout Constraint: every figure must be wrapped in `\begin{figure}[H]` and every table in a `tabularx` environment, max one figure/table per section
> — replace the citation allow-list in the prompt with the exact 30 curated keys
> — add sanitizer fixes: ragged2e typo normaliser, tabularx/tabular mismatch fix, unclosed axis injector, titlepage-awareness (body-only patching), bare `&` in TikZ node labels fix

### What was built
- **`results/references.bib`** — completely rewritten: 30 curated entries only (11 `@article` with DOIs, 3 `@book`, 16 `@misc` with specific deep-link URLs; 0 root-domain URLs)
- **`src/article_writer/latex/latex_sanitizer.py`** — 12-step deterministic sanitizer pipeline (`_fix_malformed_envs` handles 6 sub-patterns 0a–0f, `_fix_missing_ragged2e`, `_fix_table_alignment` body-only, `_fix_arrow_labels`, `_fix_invalid_cite_keys`)
- **`src/article_writer/writing/_draft_prompt.py`** — updated preamble template, 4-column tabularx rule, Verification Constraint, Structural Code Alignment, and LaTeX Layout Constraint hard-rules
- **`_CURATED_KEYS` frozenset** — 30-key allowlist mirrored in both sanitizer and draft prompt

---

## Prompt 4 — Arrow Label Overlap + Citation Metadata Quality

> better now for the next bug: in figure 2 the words are not fitting the arrow so they are overlap with the boxes add a restriction for the latex "tell LaTeX to split the arrow path or set a transparent background shape behind the text label so it automatically clears out a clean gap for the words." and add more ensurment to Scan the compiled document for any raw alpha-text keys in brackets (e.g., [text]). If found, locate the matching key in the .tex file and force the reference module to build a proper BibTeX entry for it but most important to make sure "Every entry in the References list must contain a complete academic metadata footprint: Author name, Article Title, Journal or Institutional Publisher, Year, and a specific, verified deep-link URL. Do not generate placeholder domains or root-level marketing links." do a prd and a plan and a todo list and excecute it and do not ruin what we have improved!

### What was built
- **Arrow label clearance** — `_fix_arrow_labels()` in sanitizer injects `fill=white, inner sep=2pt, font=\footnotesize` into every TikZ `\draw[->] node[...]` edge label; hard-rule added to prompt
- **`[?]` artifact detection** — `validate()` scans the lualatex `.log` for "Reference ... undefined" and "Citation ... undefined" warnings
- **Citation stub quality** — `_KNOWN_DOMAIN_META` dict (30+ entries) in `latex_compiler.py` maps domain → `(org_name, article_title, url_path)` to generate proper academic stubs with `author`, `title`, `institution`, `year`, `url`, `note` fields; no root-domain URLs in stubs
- **`_is_root_domain_url()`** — validator helper that rejects bare `https://www.domain.com` URLs in bib entries
- PRD written to `docs/arrow_citation_prd.md`; all items marked complete

---

## Prompt 5 — Block Citation Allow-List Violations at Prompt Level

> fix The LLM still sometimes ignores the citation allow-list — now handled silently by `_fix_invalid_cite_keys()` rather than blocked at the prompt level for the writer

### What was built
- **`⚠ CITATION KEYS — HARD STOP`** block added at the top of `DRAFT_SYSTEM_PROMPT` HARD RULES section — lists all 30 curated keys in compact form with ✓/✗ examples
- **`_repair_cite_keys()` self-correction pass** added to `DraftGenerator.generate()` — immediately after LLM response, before any sanitizer: detects invalid `\cite{}` keys, sends a targeted correction prompt to the LLM with the bad key list, falls back to the original source if the LLM repair makes things worse
- **Safety check** — if the repaired source has equal or more invalid keys, the original is kept and the sanitizer's `_fix_invalid_cite_keys()` handles it as a final safety net

---

## Prompt 6 — Full Pipeline Runs (Iterative Testing)

> now run the full pipeline

Run 3 times across Sessions 3–5 to catch and fix bugs:
- **Run 1** → found: `\usepackage{ragged2ce}` typo (fatal), tabularx/tabular mismatch on titlepage, missing `\end{axis}` in pgfplots
- **Run 2** → found: bare `&` in TikZ `\node{...}` labels causing "Misplaced alignment tab" errors; 26 auto-generated domain stubs contaminating bib
- **Run 3** → clean: 0 fatal LaTeX errors, 0 validation issues, 0 citation stubs generated, citation repair caught 3 invalid keys and fixed them to 0

Final result: 24-page PDF (lualatex, 0 errors, 0 `[?]` artifacts).

---

## Prompt 7 — LaTeX Chart Self-Check Tool

> add a tool for me that build a chart in latex I want it for self checking so the tool use one of the examples in our data, no API calls and build a chart for some paragraph with data

### What was built
**`src/article_writer/tools/chart_checker.py`** — zero-API CLI tool:

1. Reads `results/draft_final.tex` — extracts the first pgfplots `ybar` axis: tick labels, series names, coordinate data
2. Reads `data/research.md` — extracts quantitative percentage facts using regex (52% drug alert reduction, 67% denial reduction)
3. Supplements with 3 hardcoded values from curated `@article` references (esteva 91%, rajpurkar 90.3%, campanella 98.8%)
4. **Structural Code Alignment check** — for each axis tick label, checks verbatim appearance in the 3 paragraphs preceding the figure in the draft; prints PASS/FAIL per label
5. Generates a standalone lualatex document (2 pages): page 1 = draft figure reproduced + PASS/FAIL table + prose context; page 2 = research facts bar chart + source sentences
6. Compiles to `results/chart_check/chart_check.pdf` — no LLM calls, no network calls

```bash
uv run python src/article_writer/tools/chart_checker.py
# Output: results/chart_check/chart_check.pdf
```

---

## Prompt 8 — Grade Fixes: Tests, Coverage, Jupyter Notebook, Python Graph

> (Session continuation) Fix 13 failing tests. Boost coverage from 24.49% to ≥85%. Run the Python graph and wire into draft. Create Jupyter notebook for results analysis. Commit and push.

### What was built
- **Test fixes** — all mock helpers updated to return `LLMResponse(text, input_tokens, output_tokens, model, cost_usd)` instead of Anthropic-style `MagicMock`; spurious `anthropic.Anthropic` patches removed; Google SDK mock updated from `google.generativeai` (old) to `google.genai` (new)
- **New test files** — `test_latex_sanitizer.py`, `test_latex_sanitizer_fixes.py`, `test_latex_sanitizer_validate.py`, `test_latex_sanitizer_extra.py`, `test_sdk.py`, `test_chart_checker.py`, `test_guideline_generator.py`
- **Coverage** — 24.49% → 86.48% (303 tests passing)
- **`notebooks/results_analysis.ipynb`** — 10-cell notebook: latency boxplot by category, token usage, cumulative cost, cost pie, model comparison, top-10 expensive steps, latency histogram
- **`assets/graphs/accuracy_curve.pdf`** — matplotlib graph generated and inserted into `results/draft_final.tex` via `\includegraphics`

| Decision | Detail |
|---|---|
| Mock return type | `LLMResponse` dataclass (not `MagicMock` with `.content[0].text`) |
| SDK test patching | Lazy local imports in SDK methods → patches target original module paths |
| Coverage tool | `pytest-cov` with `--cov-fail-under=85` in `pyproject.toml` |

---

## Prompt 9 — Python-First Chart Generation Pipeline

> is it now in the pipeline instead of generating the graphs and the charts using python code and then taking the images as the output of this code and inserted in the latex draft as image? … make a prd file for this addition then a plan then a todo list and execute it fully

### What was built
- **`src/article_writer/tools/chart_generator.py`** — generates 3 publication-quality matplotlib PDFs before LLM runs:
  - `accuracy_curve.pdf` — training vs validation accuracy over 30 epochs
  - `diagnostic_comparison.pdf` — AI vs human expert on 5 medical imaging tasks
  - `cost_reduction.pdf` — operational cost reduction across hospital departments
  - `generate_all()` is idempotent (skips existing unless `regenerate=True`)
- **Sanitizer Fix n3 updated** — `_fix_includegraphics` now accepts `tex_dir: Path | None`; skips replacement when the referenced PDF exists on disk
- **Draft prompt updated** — removed "NEVER use `\includegraphics`" rule; added PRE-GENERATED CHARTS block listing all 3 PDF paths with descriptions
- **SDK wired** — `start_writing_session()` calls `generate_all(Path(charts_dir))` before `DraftGenerator` runs
- **`pyproject.toml`** — added `matplotlib>=3.8.0` and `numpy>=1.26.0`
- **Tests** — `test_chart_generator.py` (8 tests), sanitizer T1/T2 in `test_latex_sanitizer_extra.py`

| Decision | Detail |
|---|---|
| Why pre-generate | Matplotlib produces clean, anti-aliased PDFs; pgfplots is error-prone and hard for LLMs |
| Idempotency | `generate_all()` checks `path.exists()` before calling each generator — safe to call on every run |
| Sanitizer bypass | File-existence check before replacement so pre-generated charts are never converted to pgfplots |
| LLM instruction | Prompt tells LLM the exact paths; LLM uses `\includegraphics[width=0.88\textwidth]{../assets/graphs/<file>.pdf}` |

---

## Prompt 10 — TikZ Spatial Collision Prevention

> modify the writer agent to "When generating TikZ code for flowcharts or system architectures, you must ensure that lines never cross through text labels or box borders…" and for the reviewer "Analyze the layout architecture of the generated TikZ code and check for spatial collisions…" make a prd file and a plan and todo list and execute it to solve the figure bug

### What was built
- **Writer prompt §3 TIKZ FLOWCHART RULES** — new block in CONTENT REQUIREMENTS with:
  - Label clearance: every `node[midway]` must carry `fill=white, inner sep=2pt`
  - Three safe feedback-loop routing methods with copy-paste examples (`|-`, `to[out,in]`, named waypoint coordinate)
  - `xshift ≥ 1.5cm` beyond rightmost box edge for return paths
  - Complete clean flowchart example with orthogonal feedback loop
- **HARD RULES strengthened** — three numbered constraints replacing the single arrow-label line
- **Reviewer `TikzLayout` check** (priority 3) — rejects figures where:
  - Connection label node lacks `fill=white` or `fill=pagecolor`
  - `\draw` path uses bare `--` for multi-hop route crossing a box
- **Editor priority updated** — TikZ fixes now ranked 2nd (after BiDi, before Coverage); `_format_comments` priority_order includes `"TikzLayout"`
- **Sanitizer Fix 12 `_fix_diagonal_paths`** — converts `-- ++(x,y)` diagonal segments to `-- ++(x,0) -- ++(0,y)` (horizontal-first orthogonal routing)
- **Tests** — `tests/unit/test_latex/test_tikz_collision.py` (11 tests)
- **Verified in pipeline run** — generated flowchart uses `(feedback.east) -- ++(2.5cm,0) |- (integration.east)` with `fill=white` on all labels

| Decision | Detail |
|---|---|
| Three-layer defence | Prompt (prevent) → reviewer (detect) → sanitizer (fix) — collision never reaches PDF |
| Diagonal detection | Regex `-- \+\+\(x,y\)` where both x and y non-zero; split to `-- ++(x,0) -- ++(0,y)` |
| Orthogonal routing | `|-` operator routes horizontal then vertical; `xshift` keeps the line clear of box borders |
