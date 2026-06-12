# PRD — Researcher Agent
**Per-Mechanism Product Requirements**

| Field | Value |
|---|---|
| Version | 1.00 |
| Mechanism | ResearcherAgent |
| File | `src/article_writer/agents/researcher_agent.py` |

## Scope
The ResearcherAgent is responsible for gathering, verifying, filtering, and archiving web research material. It is the only agent with external tool access (4 MCP-backed tools). It operates in an exploratory, human-in-the-loop mode.

## Inputs
| Input | Source | Format |
|---|---|---|
| `guideline.md` | Human-written | Markdown — Topic, Angle, Key Points, Narrative Arc |
| Human feedback | Manager (interactive) | Free text after each batch |

## Behavior Steps
1. Parse `guideline.md` to extract topic and research dimensions
2. Call `researcher_handler` with current intent → receive 3-5 suggested queries
3. For each query: call `deep_research(prompt=query)` → get answer + citations
4. For each returned source: call `citation_extractor(prompt=url_or_text)` → formatted citation
5. For each content chunk: call `content_filter(prompt="content | Topic: topic")` → keep/discard
6. Pause after every 5 queries — present findings to human manager
7. Receive human feedback — pivot or confirm via `researcher_handler`
8. After human approval: write all HIGH/MEDIUM facts to `data/research.md`

## Tools Used
| Tool | Call Pattern | When |
|---|---|---|
| `researcher_handler` | `prompt = current research intent` | Before each batch to plan queries |
| `deep_research` | `prompt = exact query string` | For each planned query |
| `citation_extractor` | `prompt = URL or text passage` | For each returned source |
| `content_filter` | `prompt = "content | Topic: topic"` | For each content chunk before storing |

## Human-in-the-Loop Points
- After every batch of 5 queries (configurable via `research.batch_size`)
- Before writing `research.md` (human must approve)

## Output Artifact
`data/research.md` — structured markdown with:
- ≥ 10 cited facts (HIGH or MEDIUM confidence only)
- Sections per research dimension
- Inline citations per fact

## Acceptance Criteria
- AC-R1: Produces `data/research.md` with ≥ 10 facts
- AC-R2: No LOW confidence content in artifact
- AC-R3: Every fact has inline `[title](url)` citation
- AC-R4: Human feedback loop pauses after each 5-query batch
- AC-R5: Tool call sequence follows: researcher_handler → deep_research → citation_extractor → content_filter
