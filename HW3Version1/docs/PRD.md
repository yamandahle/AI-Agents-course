# PRD — AI Article-Writing Multi-Agent Network
**Product Requirements Document**

| Field | Value |
|---|---|
| Project | HW3 — Mass Production of AI Agents |
| Version | 1.00 |
| Author | Nagham (Manager) + Claude (Engineer) |
| Date | 2026-06-11 |
| Course | AI Agents Course — Dr. Yoram Segal |
| Stage | 1 — Architecture Definition |

---

## 1. Project Overview

### 1.1 Problem Statement
Writing a professional 15-page academic article requires iterative research, structured composition, quality critique, and precise formatting. Doing this manually is slow. Doing it with a single LLM prompt produces shallow, unreliable output with no source traceability.

### 1.2 Solution
A two-agent CrewAI network where a **Researcher** and a **Writer** collaborate through a shared context store. The Researcher gathers, filters, and archives verified material via MCP-backed web search tools. The Writer loads that material plus static writing profiles and few-shot examples, generates a LaTeX draft, and refines it through an evaluator-optimizer loop before human final review.

### 1.3 Project Stages
| Stage | Name | Description |
|---|---|---|
| 1 | Architecture Definition | PRD, PLAN, TODO (current stage) |
| 2 | Implementation | Code, MCP wiring, LaTeX pipeline |
| 3 | Evaluation & Submission | Testing, quality checks, PDF output |

---

## 2. Target Users & Stakeholders

| Role | Person | Involvement |
|---|---|---|
| Manager / Product Owner | Nagham | Defines requirements, approves research batches, does final article review |
| Engineer | Claude (AI) | Implements agents, MCP tools, LaTeX pipeline |
| Evaluator | Course Grader / Dr. Segal | Grades final PDF article |

---

## 3. Functional Requirements

### 3.1 Researcher Agent

#### 3.1.1 Inputs
- `guideline.md` — human-written article guideline (topic, angle, key points, narrative arc)
- Human feedback messages after each search batch

#### 3.1.2 Behavior
1. Parse `guideline.md` to extract the topic and research dimensions.
2. Execute an initial batch of targeted web searches via MCP tools (Gemini or Perplexity).
3. Pause and surface gathered material to the human for feedback.
4. Based on feedback: pivot, deepen, or confirm the research direction.
5. Repeat steps 2–4 until human approves the research batch.
6. Filter all collected material: remove untrustworthy content, remove duplicates, keep only the most relevant facts, quotes, and citations.
7. Write the curated material to `research.md` (final research artifact).

#### 3.1.3 Tools (via MCP Server)
| Tool Name | Description | Query Construction |
|---|---|---|
| `deep_research` | Calls Gemini/Perplexity for deep search | Prompt = research query string |
| `researcher_handler` | Manages multi-turn search session, tracks visited URLs | Prompt = current research intent |
| `citation_extractor` | Extracts and formats citations from returned pages | Prompt = URL or raw text |
| `content_filter` | LLM-based relevance and trust scoring | Prompt = content chunk + topic |

#### 3.1.4 Human-in-the-Loop Points
- After every search batch (configurable: default = 5 queries)
- Before writing `research.md` (final approval)

#### 3.1.5 Output Artifact
`research.md` — structured markdown file containing:
- Section per research dimension
- Bullet-point facts with inline citations `[source](url)`
- Confidence score per fact (HIGH / MEDIUM — LOW content is discarded)
- Raw source URLs for reproducibility

---

### 3.2 Writer Agent

#### 3.2.1 Inputs (Phase 1 — Context Load)
| File | Type | Purpose |
|---|---|---|
| `guideline.md` | Dynamic (human-written) | WHAT to write: topic, angle, key points, narrative arc |
| `research.md` | Dynamic (Researcher output) | WHAT to draw on: verified facts and citations |
| `profiles/Structure.md` | Static | HOW to write: document structure template |
| `profiles/Terminology.md` | Static | HOW to write: vocabulary, register, style rules |
| `profiles/Characters.md` | Static | HOW to write: voice, persona, tone |
| `few_shot_examples/` | Static | Example article sections demonstrating the expected output quality |

#### 3.2.2 Phase 2 — Initial Draft Generation
- Combine all context into a structured Writer Prompt.
- Call the LLM (Claude Sonnet or equivalent) to produce a complete first draft in LaTeX format.
- Output: `draft_v1.tex`

#### 3.2.3 Phase 3 — Evaluator-Optimizer Loop
| Step | Actor | Action |
|---|---|---|
| Evaluate | Evaluator sub-agent | Score draft on: coverage, accuracy, style, structure, citation quality |
| Critique | Evaluator sub-agent | Produce structured critique in `critique.md` |
| Optimize | Writer sub-agent | Revise `draft.tex` based on critique |
| Repeat | Loop controller | Run until score ≥ threshold OR max iterations reached |
| Human review | Manager | Final read of the polished draft |

#### 3.2.4 Output
- `article_final.tex` — polished LaTeX source
- `article_final.pdf` — compiled PDF (via LuaLaTeX + MiKTeX)

---

### 3.3 Shared Context

| Mechanism | Description |
|---|---|
| CrewAI Task context chain | `context=[research_task]` in write_task — output of Researcher becomes input of Writer |
| Shared file system | `research.md`, `guideline.md` readable by both agents |
| Crew-level shared memory | Single CrewAI `Crew` instance wraps both agents |

---

## 4. Article Content Requirements (from Assignment PDF)

### 4.1 Length & Language
- **Minimum 15 pages** (Hebrew counts harder → higher value per page)
- Language: Hebrew and/or English (BiDi mixed is required in at least one chapter)

### 4.2 Mandatory Structural Elements
| Element | Requirement |
|---|---|
| Cover Page | Topic, author name, date, course name, lecturer name |
| Table of Contents | Linked to chapters |
| Chapter Division | Logical sections with numbered headings |
| Headers & Footers | Running title + page number |
| Bibliography | At end, with linked inline citations |

### 4.3 Mandatory Content Elements
| Element | Minimum Count | Notes |
|---|---|---|
| Image | 1 | Embedded figure with caption |
| Graph | 1 | Generated by Python code (TikZ or matplotlib → PDF include) |
| Table | 1 | Formatted LaTeX table |
| Mathematical Formula | 1 | Proper LaTeX math, "fancy formula" style |
| BiDi Chapter | 1 | Demonstrates correct RTL↔LTR switching |

### 4.4 LaTeX Technical Stack
| Component | Choice |
|---|---|
| Compiler | LuaLaTeX (primary) / XeLaTeX (allowed) |
| Distribution | MiKTeX |
| Bibliography | BibTeX/biber with `.bib` files |
| Graphics | TikZ for diagrams |
| Compilations | ~4 passes needed for cross-references |

---

## 5. Non-Functional Requirements

### 5.1 Code Quality (from software_submission_guidelines-V3.pdf)
| Requirement | Standard |
|---|---|
| Project structure | `src/`, `docs/`, `tests/`, `config/`, `assets/` |
| File size | Max 150 lines per code file |
| Architecture | SDK layer for all business logic |
| OOP | No code duplication; use mixins and base classes |
| API calls | All external calls through centralized `ApiGatekeeper` |
| Rate limiting | Configured in `config/rate_limits.json`, never hardcoded |
| Linter | Ruff — zero errors |
| Test coverage | ≥ 85% |
| TDD | Tests written before/alongside code (Red → Green → Refactor) |
| Secrets | No API keys in source; use `.env` + `.env-example` |
| Package manager | `uv` only (no pip direct calls) |
| Versioning | Start at 1.00; bump on significant changes |

### 5.2 Agent Security
| Threat | Mitigation |
|---|---|
| Prompt Injection | Sanitize all web-fetched content before injecting into prompts |
| Tool Misuse | Scope MCP tools to read-only search; no file deletion tools exposed |
| Identity Abuse | API keys in environment only; no agent-to-agent key passing |
| Memory Poisoning | Research content validated by `content_filter` tool before storage |

### 5.3 Observability
- All MCP tool calls logged with timestamp, query, response length, cost
- Evaluator loop: score per iteration logged to `results/eval_log.json`
- Token usage tracked per agent call

### 5.4 Performance & Cost
- Rate limits: configured per API (Gemini, Perplexity, LLM provider)
- Queue management: FIFO queue when rate limit hit
- Cost tracking: input + output tokens logged per run

---

## 6. Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| AC-01 | Researcher produces `research.md` with ≥ 10 cited facts | File inspection |
| AC-02 | Writer produces a LaTeX file that compiles to PDF without errors | `lualatex` exit code = 0 |
| AC-03 | PDF is ≥ 15 pages | Page count |
| AC-04 | Cover page, TOC, bibliography present | Visual inspection |
| AC-05 | At least 1 image, 1 graph, 1 table, 1 formula in PDF | Visual inspection |
| AC-06 | At least 1 BiDi chapter present | Visual inspection |
| AC-07 | Ruff check passes with 0 errors | `ruff check src/` |
| AC-08 | Test coverage ≥ 85% | `uv run pytest --cov` |
| AC-09 | No API keys in source code | `git grep -r "API_KEY\s*="` returns nothing |
| AC-10 | All files ≤ 150 lines | automated file size check |
| AC-11 | Evaluator loop runs ≥ 2 iterations before human review | Log inspection |
| AC-12 | MCP tools respond with citations | Tool output inspection |

---

## 7. Out of Scope (Stage 1)

- Actual implementation code (Stage 2)
- Final article topic selection (human decision)
- Deployment to cloud / production infrastructure
- GUI or web interface

---

## 8. Dependencies & Assumptions

| Item | Detail |
|---|---|
| Gemini API key | Must be provided in `.env` |
| Perplexity API key | Must be provided in `.env` (fallback if Gemini unavailable) |
| LLM provider key | Claude API key in `.env` |
| MiKTeX installed | On the WSL Ubuntu machine |
| Python ≥ 3.10 | Required by CrewAI and uv |
| uv installed | Global install on machine |
| WSL Ubuntu | Development environment per course guidelines |

---

## 9. Milestones

| Milestone | Deliverable | Stage |
|---|---|---|
| M1 — Architecture | PRD, PLAN, TODO, promptsUsed | Stage 1 (current) |
| M2 — Skeleton | Project structure, MCP server wired, agents defined | Stage 2 |
| M3 — Researcher Live | Researcher agent completes a research run end-to-end | Stage 2 |
| M4 — Writer Live | Writer agent produces a compiling LaTeX draft | Stage 2 |
| M5 — Loop Live | Evaluator-optimizer loop runs ≥ 2 iterations | Stage 2 |
| M6 — Full Run | End-to-end run produces a ≥15 page PDF | Stage 3 |
| M7 — Submission | All quality checks pass; PDF submitted | Stage 3 |
| M8 — Review Loop | 3–4 cycle Reviewer↔Editor with version files | Stage 3 |
| M9 — Eval Dataset | 20 labelled articles, judge F1 ≥ 0.80 on test | Stage 3 |

---

## 10. Stage 3 Extension — New Requirements

### 10.1 LLM Provider Abstraction
- `LLMClient` wraps Anthropic Claude and Google Gemini behind one `complete()` interface
- Provider selected by `LLM_PROVIDER` env var (overrides `config/setup.json["llm"]["provider"]`)
- Anthropic model: `claude-sonnet-4-6` | Google model: `gemini-1.5-pro`
- All calls automatically logged to `traces.jsonl` + `metrics.jsonl`

### 10.2 PDF Few-Shot Examples
- `few_shot_examples/` now contains 3 real MDPI PDFs (not markdown)
- `FewShotLoader` reads PDFs via PyMuPDF (`fitz`); supports `.pdf`, `.md`, `.txt`
- Injected into Writer and Editor contexts only — Reviewer never receives few-shots

### 10.3 Reviewer (Isolated Context)
**Receives:** draft + guideline + research + profiles
**Does NOT receive:** few-shot examples, writer system prompt, writer's few-shot context
**Output:** `ArticleReview(comments: list[ReviewComment], overall_score: float, pass_fail: str)`
**Each `ReviewComment`:** `profile` (which rule), `location` (where in article), `comment` (what's wrong)

### 10.4 Editor (Full Context)
**Receives:** draft + structured reviews + guideline + research + profiles + few-shots
**Priority order:** guideline violations → research accuracy → profile violations
**Output:** next draft version saved to `results/draft_v{N+1}.tex`

### 10.5 Observability
- `results/traces.jsonl` — full I/O per LLM/tool call (ts, step, provider, model, tokens, input, output)
- `results/metrics.jsonl` — latency, tokens, cost per step (ts, step, model, latency_ms, cost_usd)

### 10.6 Eval Dataset
- Extract 20 MDPI articles (13–20 pages) via `ArticleExtractor`
- Auto-label with LLM: binary PASS/FAIL + 3-sentence critique
- Split: ~80% train / ~10% dev / ~10% test → saved as `eval_dataset/splits/{split}.jsonl`
- `ArticleJudge` predicts PASS/FAIL per article
- `JudgeLoop` refines judge prompt on dev split (F1 target ≥ 0.80)
- Final validation on test split (never used during refinement)

### 10.7 Acceptance Criteria (Stage 3)
| ID | Criterion |
|---|---|
| AC-S3-01 | `LLMClient` supports both Anthropic and Google without code changes |
| AC-S3-02 | `LLM_PROVIDER` env var overrides config at runtime |
| AC-S3-03 | `FewShotLoader` reads PDF files via PyMuPDF |
| AC-S3-04 | Reviewer receives ONLY draft + guideline + research + profiles |
| AC-S3-05 | Every review cycle saves `review_v{N}.json` with valid `ArticleReview` JSON |
| AC-S3-06 | `draft_final.tex` is always written at end of review loop |
| AC-S3-07 | Every LLM call writes one record to `traces.jsonl` |
| AC-S3-08 | Every LLM call writes one record to `metrics.jsonl` with cost |
| AC-S3-09 | Eval dataset saved as JSONL with train/dev/test splits |
| AC-S3-10 | JudgeLoop runs ≥ 1 iteration on dev; always runs final pass on test |
