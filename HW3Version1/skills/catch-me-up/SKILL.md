---
name: catch-me-up
description: Quick project orientation skill — triggered when the user types "catch me up". Delivers a one-screen summary of the project status, directory tree, agents, and tools.
metadata:
  author: article-writer-system
  version: "1.0"
  agent: all
  trigger: phrase "catch me up"
---

## Catch-Me-Up — Instructions

### Trigger
This skill activates **only** when the user types the exact phrase: **"catch me up"**
Do not activate on similar phrases like "what's going on", "update me", or "summarize".

### Response Format
When triggered, respond with the following structure (must fit in ≤ 80 lines):

```
=== ARTICLE WRITER — PROJECT STATUS ===

PROJECT: AI-powered 2-agent network to write a 15-page academic article in LaTeX
CURRENT STAGE: {Stage 1 | Stage 2 | Stage 3} — {description}
NEXT ACTION: {what needs to be done next}

--- DIRECTORY TREE ---
HW3Version1/
├── src/article_writer/     # All Python source code
│   ├── agents/             # ResearcherAgent, WriterAgent (+ Evaluator sub-agent)
│   ├── tasks/              # CrewAI Task definitions (research + writing phases)
│   ├── tools/              # 4 MCP-backed tools for web search and filtering
│   ├── mcp/                # Gemini + Perplexity API clients + MCP server
│   ├── writing/            # Context loader, draft generator, evaluator, optimizer
│   ├── latex/              # LaTeX compiler, templates, BiDi handler
│   ├── shared/             # Gatekeeper, config, logger, constants, version
│   └── sdk/                # ArticleWriterSDK — single public entry point
├── tests/                  # Unit + integration tests (TDD, ≥85% coverage)
├── docs/                   # PRD, PLAN, TODO, per-mechanism PRDs
├── config/                 # setup.json + rate_limits.json (versioned 1.00)
├── profiles/               # Writing profiles: Structure.md, Terminology.md, Characters.md
├── skills/                 # research/, writing/, catch-me-up/ SKILL.md files
├── few_shot_examples/      # Example LaTeX sections injected into writer prompt
├── data/                   # guideline.md (human input) + research.md (researcher output)
├── assets/                 # images/ + graphs/ (generate_graph.py)
├── results/                # Draft .tex files, final PDF, eval_log.json, run_log.txt
└── skills.md + tools.md    # Summary of all skills and tools

--- AGENTS ---
1. ResearcherAgent  — Exploratory, human-in-the-loop after each search batch
                      Tools: deep_research, researcher_handler, citation_extractor, content_filter
2. WriterAgent      — Deterministic, 3-phase pipeline, human review at end only
                      Tools: none (uses context only)
3. EvaluatorAgent   — Sub-agent of Writer, scores draft on 5 dimensions, writes critique

--- TOOLS ---
1. deep_research        — Calls Gemini (fallback: Perplexity) for web search with citations
2. researcher_handler   — Manages search session, avoids duplicate queries
3. citation_extractor   — Formats URL or text into markdown citation
4. content_filter       — Scores content as HIGH/MEDIUM/LOW confidence, discards LOW

--- PIPELINE ---
Researcher: guideline.md → batch searches → human feedback → research.md
Writer:     research.md + profiles + few-shots → draft.tex → eval loop → PDF

=== END STATUS ===
```

### Constraints
1. **Output must fit in ≤ 80 lines.** Cut detail if necessary — breadth over depth.
2. **Trigger phrase is exactly "catch me up"** — case-insensitive, but otherwise exact.
3. **Always state current stage and next action.** These are the most important lines.
4. **Do not list all 800 TODO items.** Only the next immediate action.
5. **Keep the directory tree to 1 line per entry.** No sub-sub-entries.
6. **Never modify any files** when this skill is triggered. This is read-only orientation.
7. **Update stage dynamically.** If Stage 1 is done, say Stage 2. Do not hardcode.

### Example Trigger → Response

**User types:** `catch me up`

**Response:**
```
=== ARTICLE WRITER — PROJECT STATUS ===

PROJECT: AI 2-agent network (Researcher + Writer) → 15-page LaTeX PDF article
CURRENT STAGE: Stage 2 — Implementation (Python code + MCP tools)
NEXT ACTION: Implement src/article_writer/shared/gatekeeper.py (TODO item 107)

[... directory tree, agents, tools, pipeline as above ...]
```
