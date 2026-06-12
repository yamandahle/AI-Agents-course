# PLAN — AI Article-Writing Multi-Agent Network
**Architecture & Technical Planning Document**

| Field | Value |
|---|---|
| Version | 1.00 |
| Date | 2026-06-11 |
| Stage | 1 — Architecture Definition |

---

## 1. System Architecture Overview

### 1.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        HUMAN MANAGER                            │
│   provides: guideline.md │ approves: research batches          │
│                          │ approves: final article              │
└──────────────┬───────────────────────────┬──────────────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────┐   ┌────────────────────────────────┐
│     RESEARCHER AGENT     │   │        WRITER AGENT            │
│  (Exploratory + HITL)    │   │  (Deterministic, HITL at end)  │
│                          │   │                                │
│  1. Read guideline.md    │   │  Phase 1: Load Context         │
│  2. Batch web searches   │──▶│    guideline.md + research.md  │
│  3. Human feedback loop  │   │    profiles/ + few_shot/       │
│  4. Filter & curate      │   │  Phase 2: Generate draft.tex   │
│  5. Write research.md    │   │  Phase 3: Evaluator-Optimizer  │
└──────────┬───────────────┘   └────────────┬───────────────────┘
           │                                │
           │  MCP Server                    │  LLM Provider
           ▼                                ▼
┌──────────────────────┐       ┌────────────────────────────────┐
│   MCP TOOL LAYER     │       │    LATEX PIPELINE              │
│                      │       │                                │
│  • deep_research     │       │  draft.tex                     │
│  • researcher_handler│       │  ──► lualatex (4 passes)       │
│  • citation_extractor│       │  ──► article_final.pdf         │
│  • content_filter    │       │                                │
│                      │       │  Evaluator sub-agent           │
│  API Backends:       │       │  scores draft, writes          │
│  • Gemini            │       │  critique.md, loops            │
│  • Perplexity        │       │                                │
└──────────────────────┘       └────────────────────────────────┘
```

### 1.2 Framework Choice: CrewAI

**Decision:** Use **CrewAI** as the agent orchestration framework.

| Option | Pros | Cons | Decision |
|---|---|---|---|
| CrewAI | Role-based agents, Task context chain, Sequential/Hierarchical process, Skills support | Less fine-grained state control than LangGraph | ✅ **Chosen** |
| LangGraph | State machines, conditional branching | More boilerplate, no built-in role system | ❌ Overkill for this 2-agent crew |
| LangChain alone | Simple pipelines | No multi-agent orchestration built in | ❌ Too basic |

**Rationale:** The assignment pseudocode in the lecture PDF uses CrewAI. The workflow is: researcher → writer → reviewer (sequential), which maps directly to `Process.sequential` in CrewAI. The evaluator-optimizer loop is internal to the Writer's task chain.

---

## 2. Project Directory Structure

```
HW3Version1/
├── src/
│   └── article_writer/
│       ├── __init__.py
│       ├── sdk/
│       │   └── sdk.py                  # Single entry point for all logic
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── researcher_agent.py     # Researcher Agent definition
│       │   └── writer_agent.py         # Writer Agent + Evaluator sub-agent
│       ├── tasks/
│       │   ├── __init__.py
│       │   ├── research_tasks.py       # Research task definitions
│       │   └── writing_tasks.py        # Writing + evaluation task definitions
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── deep_research_tool.py   # MCP deep research wrapper
│       │   ├── researcher_handler.py   # Multi-turn search session manager
│       │   ├── citation_extractor.py   # Citation formatting tool
│       │   └── content_filter.py       # LLM-based relevance filter
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── mcp_server.py           # MCP server definition
│       │   ├── gemini_client.py        # Gemini API client (via MCP)
│       │   └── perplexity_client.py    # Perplexity API client (via MCP)
│       ├── writing/
│       │   ├── __init__.py
│       │   ├── context_loader.py       # Phase 1: load all MD context files
│       │   ├── draft_generator.py      # Phase 2: generate LaTeX draft
│       │   ├── evaluator.py            # Phase 3: evaluate draft
│       │   └── optimizer.py            # Phase 3: apply critique and revise
│       ├── latex/
│       │   ├── __init__.py
│       │   ├── latex_compiler.py       # Runs lualatex compilation
│       │   ├── latex_templates.py      # LaTeX boilerplate (cover, TOC, bib)
│       │   └── bidi_handler.py         # Hebrew-English BiDi switching helpers
│       └── shared/
│           ├── __init__.py
│           ├── gatekeeper.py           # API Gatekeeper (rate limits, queuing)
│           ├── config.py               # Configuration loader
│           ├── version.py              # Version tracking (starts at 1.00)
│           └── constants.py            # Immutable project constants
│
├── tests/
│   ├── unit/
│   │   ├── test_researcher_agent/
│   │   ├── test_writer_agent/
│   │   ├── test_tools/
│   │   ├── test_mcp/
│   │   ├── test_writing/
│   │   └── test_latex/
│   ├── integration/
│   │   ├── test_researcher_to_writer.py
│   │   └── test_full_pipeline.py
│   └── conftest.py
│
├── docs/
│   ├── PRD.md                          # Product Requirements (this project)
│   ├── PLAN.md                         # This file
│   ├── TODO.md                         # 800-item task list
│   ├── PRD_researcher_agent.md         # Per-mechanism PRD: Researcher
│   ├── PRD_writer_agent.md             # Per-mechanism PRD: Writer
│   ├── PRD_mcp_tools.md                # Per-mechanism PRD: MCP Tools
│   ├── PRD_latex_pipeline.md           # Per-mechanism PRD: LaTeX
│   └── PRD_evaluator_optimizer.md      # Per-mechanism PRD: Eval loop
│
├── config/
│   ├── setup.json                      # Main app config (versioned 1.00)
│   └── rate_limits.json                # API rate limits (versioned 1.00)
│
├── data/
│   ├── guideline.md                    # Human-written article guideline (INPUT)
│   └── research.md                     # Researcher output artifact
│
├── profiles/
│   ├── Structure.md                    # HOW: Document structure rules
│   ├── Terminology.md                  # HOW: Vocabulary and style
│   └── Characters.md                   # HOW: Voice, tone, persona
│
├── few_shot_examples/
│   ├── example_intro.md                # Example article introduction
│   ├── example_section.md              # Example body section
│   └── example_conclusion.md           # Example conclusion
│
├── assets/
│   ├── images/                         # Images for LaTeX inclusion
│   └── graphs/                         # Python-generated graph PDFs
│
├── results/
│   ├── eval_log.json                   # Evaluator loop scores per iteration
│   ├── draft_v1.tex                    # Initial draft
│   ├── article_final.tex               # Final polished LaTeX
│   └── article_final.pdf               # Final compiled PDF
│
├── notebooks/
│   └── analysis.ipynb                  # Cost analysis, token usage
│
├── README.md
├── pyproject.toml
├── uv.lock
├── .env-example
└── .gitignore
```

---

## 3. Agent Architecture

### 3.1 Researcher Agent

```python
researcher = Agent(
    role="Expert Research Analyst",
    goal="Gather comprehensive, verified, cited material on the article topic",
    backstory="""You are a meticulous research analyst. You search multiple
    sources, verify facts, extract citations, and filter out untrustworthy
    content. You never skip content and never keep content below confidence
    threshold. You follow human feedback to pivot your research direction.""",
    tools=[deep_research_tool, researcher_handler, citation_extractor, content_filter],
    skills=["./skills/research"],
    allow_delegation=False,
    verbose=True,
)
```

**Human-in-the-Loop integration:** After each search batch, the task pauses and surfaces results via `Human Input` callback. The human provides feedback which becomes the next task description.

### 3.2 Writer Agent

```python
writer = Agent(
    role="Senior Technical Article Writer",
    goal="Produce a polished 15-page LaTeX article from research material",
    backstory="""You are a skilled writer who transforms research into
    well-structured, publication-quality articles. You follow writing profiles
    exactly, adhere to the given structure, and improve your work iteratively
    based on evaluator critique.""",
    tools=[],  # Writer works from context; no external tool calls
    skills=["./skills/writing"],
    allow_delegation=True,   # Can delegate to Evaluator sub-agent
    verbose=True,
)
```

### 3.3 Evaluator Sub-Agent (internal to Writer's Phase 3)

```python
evaluator = Agent(
    role="Article Quality Evaluator",
    goal="Score the draft and produce actionable critique",
    backstory="""You are a ruthless editor. You score articles on coverage,
    accuracy, style adherence, structure, and citation quality. You produce
    a structured critique that the writer can act on immediately.""",
    tools=[],
    verbose=True,
)
```

---

## 4. Task Flow

### 4.1 Research Tasks

```
research_batch_task
    ├── description: "Search for {topic}. Execute 5 queries via deep_research tool."
    ├── expected_output: "Markdown list of facts with citations"
    ├── agent: researcher
    └── human_input: True   # Pause for human feedback after each batch

research_filter_task
    ├── description: "Filter all gathered content. Remove untrustworthy items."
    ├── expected_output: "Curated research.md with HIGH/MEDIUM confidence facts only"
    ├── agent: researcher
    └── context: [research_batch_task]

research_artifact_task
    ├── description: "Write all curated content to research.md artifact."
    ├── expected_output: "Completed research.md file"
    ├── agent: researcher
    └── context: [research_filter_task]
```

### 4.2 Writing Tasks

```
context_load_task
    ├── description: "Load guideline.md, research.md, all profile files, few-shot examples."
    ├── expected_output: "Unified context string ready for draft generation"
    ├── agent: writer
    └── context: [research_artifact_task]

draft_generation_task
    ├── description: "Generate complete LaTeX article draft from context."
    ├── expected_output: "draft_v1.tex — complete LaTeX source, compilable"
    ├── agent: writer
    └── context: [context_load_task]

evaluation_task
    ├── description: "Evaluate draft on 5 dimensions. Score each 1–10."
    ├── expected_output: "critique.md with scores and specific improvement actions"
    ├── agent: evaluator
    └── context: [draft_generation_task]

optimization_task
    ├── description: "Apply critique. Revise LaTeX draft."
    ├── expected_output: "Improved draft_v{n+1}.tex"
    ├── agent: writer
    └── context: [evaluation_task]
    # Loops until score >= 8/10 OR 3 iterations reached

compilation_task
    ├── description: "Compile final LaTeX to PDF using lualatex."
    ├── expected_output: "article_final.pdf"
    ├── agent: writer
    └── context: [optimization_task]
```

---

## 5. MCP Server Architecture

### 5.1 MCP Server Definition

```
MCP Server: article-writer-research-server
├── Tool: deep_research
│   ├── Input: { "prompt": "<research query>" }
│   ├── Backend: Gemini (primary) / Perplexity (fallback)
│   └── Output: { "answer": "...", "citations": [...], "confidence": 0.0–1.0 }
│
├── Tool: researcher_handler
│   ├── Input: { "prompt": "<current research intent>" }
│   ├── State: tracks visited URLs, previous queries, session context
│   └── Output: { "new_queries": [...], "summary_so_far": "..." }
│
├── Tool: citation_extractor
│   ├── Input: { "prompt": "<URL or raw text>" }
│   └── Output: { "citation_markdown": "[Title](url)", "author": "...", "date": "..." }
│
└── Tool: content_filter
    ├── Input: { "prompt": "<content chunk> | Topic: <topic>" }
    └── Output: { "keep": true/false, "confidence": "HIGH|MEDIUM|LOW", "reason": "..." }
```

### 5.2 API Backends

| Tool | Primary | Fallback | Rate Limit |
|---|---|---|---|
| `deep_research` | Gemini 1.5 Pro | Perplexity sonar-pro | 30 req/min |
| `researcher_handler` | Internal state machine | — | N/A |
| `citation_extractor` | Gemini Flash | — | 60 req/min |
| `content_filter` | Claude Haiku | — | 60 req/min |

---

## 6. Writing Profiles Design

### 6.1 profiles/Structure.md
Defines the document skeleton: cover page, TOC, section numbering, heading hierarchy, BiDi chapter placement, bibliography position.

### 6.2 profiles/Terminology.md
Defines: accepted technical terms, preferred synonyms, terms to avoid, Hebrew transliteration conventions, citation style (IEEE vs APA).

### 6.3 profiles/Characters.md
Defines: author voice (formal academic), persona (authoritative but accessible), prohibited colloquialisms, sentence length guidelines.

### 6.4 Injection Mechanism
All three profile files are loaded in `context_load_task` and prepended to every Writer prompt as a `SYSTEM CONTEXT` block. They are never modified by agents — they are read-only static configuration.

---

## 7. Evaluator-Optimizer Loop Design

### 7.1 Evaluation Rubric

| Dimension | Weight | What is measured |
|---|---|---|
| Coverage | 25% | Does the article address all key points from guideline.md? |
| Accuracy | 25% | Are all claims backed by citations from research.md? |
| Style | 20% | Does writing match profiles/Characters.md and Terminology.md? |
| Structure | 20% | Does document follow profiles/Structure.md? |
| Citation Quality | 10% | Are citations correctly formatted and linked? |

### 7.2 Loop Control

```
score = 0
iteration = 0
max_iterations = 3
threshold = 8.0

while score < threshold and iteration < max_iterations:
    critique = evaluator.evaluate(draft)
    score = critique.weighted_score
    if score < threshold:
        draft = writer.optimize(draft, critique)
    iteration += 1

human_review(draft)  # Always: human has final word
```

---

## 8. LaTeX Pipeline Design

### 8.1 Compilation Sequence

```
1. lualatex article_final.tex      # First pass — generates .aux
2. biber article_final             # Processes .bib bibliography
3. lualatex article_final.tex      # Second pass — resolves citations
4. lualatex article_final.tex      # Third/fourth pass — resolves all cross-refs
```

### 8.2 Required LaTeX Packages

| Package | Purpose |
|---|---|
| `polyglossia` | Hebrew + English (LuaLaTeX BiDi) |
| `fontspec` | Unicode font selection |
| `geometry` | Page margins |
| `hyperref` | Linked TOC and citations |
| `biblatex` | Bibliography management |
| `tikz` | Diagrams and graphs |
| `graphicx` | Image inclusion |
| `booktabs` | Professional tables |
| `amsmath` | Mathematical formulas |
| `fancyhdr` | Headers and footers |
| `listings` | Code listings |

---

## 9. API Gatekeeper Design

Per `software_submission_guidelines-V3.pdf` section 5:

```python
class ApiGatekeeper:
    """All external API calls go through here. No direct API calls in agent code."""
    
    def execute(self, api_call, *args, **kwargs):
        # 1. Check rate limit for this service
        # 2. Queue if limit reached (FIFO queue)
        # 3. Execute with retry on transient failures (max 3 retries)
        # 4. Log: timestamp, service, tokens_in, tokens_out, cost_usd
        # 5. Return result
        ...
```

Rate limits loaded from `config/rate_limits.json` — never hardcoded.

---

## 10. SDK Architecture

Per guidelines: all business logic accessible through `SDK` class.

```
External callers (CLI / tests / notebooks)
    │
    ▼
ArticleWriterSDK          ← single entry point
    │
    ├── start_research_session(guideline_path) → research.md
    ├── start_writing_session(guideline_path, research_path) → draft.tex
    ├── run_evaluator_loop(draft_path, max_iter) → final_draft.tex
    └── compile_to_pdf(tex_path) → final.pdf
```

---

## 11. Configuration Files

### config/setup.json
```json
{
  "version": "1.00",
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-6",
    "temperature": 0.3
  },
  "research": {
    "search_backend": "gemini",
    "fallback_backend": "perplexity",
    "batch_size": 5,
    "max_batches": 10,
    "min_confidence": "MEDIUM"
  },
  "writing": {
    "max_evaluator_iterations": 3,
    "score_threshold": 8.0,
    "target_pages": 15
  },
  "latex": {
    "compiler": "lualatex",
    "compile_passes": 4
  }
}
```

### config/rate_limits.json
```json
{
  "version": "1.00",
  "services": {
    "gemini": {
      "requests_per_minute": 30,
      "requests_per_hour": 500,
      "concurrent_max": 3,
      "retry_after_seconds": 30,
      "max_retries": 3
    },
    "perplexity": {
      "requests_per_minute": 20,
      "requests_per_hour": 300,
      "concurrent_max": 2,
      "retry_after_seconds": 30,
      "max_retries": 3
    },
    "anthropic": {
      "requests_per_minute": 50,
      "requests_per_hour": 1000,
      "concurrent_max": 5,
      "retry_after_seconds": 10,
      "max_retries": 3
    }
  }
}
```

---

## 12. Security Design

| Risk | Mitigation |
|---|---|
| API keys exposed | `.env` only; `.gitignore` includes `.env`; `.env-example` with placeholders committed |
| Prompt injection via web content | `content_filter` tool sanitizes before injection; raw fetched content never goes directly into prompts |
| Runaway API costs | `ApiGatekeeper` enforces hard rate limits; cost logged per call |
| Unverified research in article | `confidence_filter` removes LOW-confidence items; human approves research before writing starts |

---

## 13. Architecture Decision Records (ADRs)

### ADR-001: Use CrewAI over LangGraph
- **Decision:** CrewAI Sequential process
- **Rationale:** Assignment PDF uses CrewAI pseudocode; role-based system fits researcher/writer/evaluator naturally; Skills system aligns with injection of writing profiles
- **Trade-off:** Less state machine control; acceptable given simple 2-agent linear flow

### ADR-002: MCP server for search tools
- **Decision:** Implement MCP server wrapping Gemini + Perplexity
- **Rationale:** Lecture L06 explicitly recommends MCP for tool integration; decouples search backend from agent logic; API updates transparent to agents
- **Trade-off:** More infrastructure setup vs. direct API calls

### ADR-003: Static writing profiles (not dynamic)
- **Decision:** `profiles/Structure.md`, `Terminology.md`, `Characters.md` are read-only
- **Rationale:** Writer agent must not alter its own style guide mid-session; separation between "what to write" (dynamic) and "how to write" (static) is clean
- **Trade-off:** No self-improving style guide; acceptable for a course assignment

### ADR-004: LuaLaTeX for Hebrew support
- **Decision:** LuaLaTeX (primary), XeLaTeX (allowed)
- **Rationale:** Assignment PDF explicitly recommends LuaLaTeX for Hebrew BiDi support; `polyglossia` package handles RTL/LTR switching
- **Trade-off:** Slower than pdfLaTeX; acceptable given article length

### ADR-005: Evaluator as sub-agent (not separate CrewAI Agent)
- **Decision:** Evaluator runs as a delegated task within the Writer's scope
- **Rationale:** Evaluator does not need external tool access; it only reads the draft; delegating keeps crew size minimal and context focused
- **Trade-off:** Evaluator shares Writer's context window; acceptable given 15-page limit

---

## Stage 3 Extension — Implementation Plan

### S3-A: LLM Abstraction Layer
**File:** `src/article_writer/shared/llm_client.py`
- `LLMClient(provider, model)` — lazy SDK import at init
- `complete(system, user, step, temperature, max_tokens) -> LLMResponse`
- Provider resolved: `LLM_PROVIDER` env var → `config.llm.provider`
- Injects tracing and metrics automatically on every call

### S3-B: PDF Few-Shot Loading
**File:** `src/article_writer/writing/few_shot_loader.py`
- `FewShotLoader(directory)` — handles `.pdf`, `.md`, `.txt`
- Uses `fitz.open()` for PDF text extraction; gracefully handles errors
- `build_context_block()` → formatted string with named headers
- Max 8000 chars per example to control context window

### S3-C: Tracing + Metrics
**Files:** `shared/tracer.py`, `shared/metrics_tracker.py`
- Both append to JSONL files — no database dependency
- Tracer: full I/O + metadata; truncates to 6000 chars each side
- Metrics: latency_ms, tokens, cost_usd; `summary()` aggregates totals
- Paths configurable via `TRACES_FILE` / `METRICS_FILE` env vars

### S3-D: Review Loop (Reviewer + Editor)
**Files:** `writing/reviewer.py`, `writing/editor.py`, `writing/review_loop.py`
- Reviewer loads ONLY: draft, guideline, research, profiles (strict isolation)
- Reviewer outputs `ArticleReview` (Pydantic BaseModel, JSON-parsed from LLM)
- Editor sorts comments by priority before sending to LLM
- `ReviewLoop.run()` manages version tracking; writes `draft_final.tex` always

### S3-E: Eval Dataset + Judge
**Files:** `eval/article_extractor.py`, `eval/dataset_builder.py`, `eval/judge.py`, `eval/f1_metrics.py`, `eval/judge_loop.py`
- `ArticleExtractor` parses abstract/keywords/sections from MDPI PDFs
- `DatasetBuilder` labels articles with LLM; splits 80/10/10
- `ArticleJudge` → `JudgeResult(verdict, confidence, critique, dimension_scores)`
- `compute_f1` — standard 2PR/(P+R) formula
- `JudgeLoop` refines prompt until F1 ≥ 0.80 or max 5 iterations

### ADR-006: Reviewer context isolation (strict)
- **Decision:** `Reviewer` class never instantiates `FewShotLoader`
- **Rationale:** Reviewer must judge quality against objective criteria (guideline, research), not against example style; mixing would bias it toward format over substance
- **Trade-off:** Reviewer cannot use examples to calibrate its expectations — acceptable because the guideline explicitly encodes requirements

### ADR-007: JSONL for traces/metrics (not SQLite)
- **Decision:** Append-only `.jsonl` files
- **Rationale:** No extra dependency, grep-able, portable, easy to read with `json.loads` per line
- **Trade-off:** No indexing or query engine — acceptable since we only need to read/summarise at the end

### ADR-008: F1 as convergence signal for judge
- **Decision:** F1 ≥ 0.80 on dev split triggers early stop
- **Rationale:** 0.80 balances precision and recall; avoids over-optimising for one metric
- **Trade-off:** Dev split is small (~2–3 articles); real convergence signal is noisy — mitigated by max_iterations cap
