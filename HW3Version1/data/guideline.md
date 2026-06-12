# Article Guideline — AI Agents in Adaptive Learning Systems

## Topic
**Title:** Adaptive Learning Facilitation Through Multi-Agent AI Systems: A Framework for Personalised Instruction and Automated Content Generation

## Target Journal
MDPI *Behavioral Sciences* or *Information* — open-access, peer-reviewed.

## Angle
Empirical-theoretical hybrid: propose a conceptual framework for deploying LLM-based agents (Researcher + Writer) in educational settings, supported by quantitative results from a pilot study on learning-outcome improvement and time-to-completion reduction. Position multi-agent AI as a measurable productivity and quality amplifier, not merely a novelty.

## Abstract (Structure Target)
Four-sentence abstract:
1. Problem statement (the gap in personalised adaptive learning at scale).
2. Proposed solution and methodology (multi-agent AI network with LLM orchestration).
3. Key results (e.g., X% accuracy on generated exercises, Y% reduction in teacher workload).
4. Conclusion sentence linking to broader AI-in-education implications.

**Keywords (6–8):** multi-agent systems; large language models; adaptive learning; personalised instruction; automated content generation; educational technology; human-in-the-loop; evaluation framework

## Required Sections (IMRAD + Extended)
| Section | Minimum Length | Key Content |
|---|---|---|
| 1. Introduction | 600 words | Research gap, objectives, article structure |
| 2. Related Work | 500 words | Prior LLM-in-education studies, agent systems, HITL literature |
| 3. Materials and Methods | 700 words | Agent architecture, LLM configs, dataset, evaluation protocol |
| 4. Results | 600 words | Quantitative findings, tables, figures |
| 5. Discussion | 500 words | Interpretation, limitations, comparison with baselines |
| 6. Conclusions | 300 words | Summary of contributions, practical implications, future work |
| Acknowledgements | 1 paragraph | Author contributions, funding |
| References | ≥25 citations | Numbered [N] style, MDPI reference format |

## Key Points (must all appear in the article)
1. Multi-agent systems reduce hallucination rates compared to single-agent baselines through mutual verification and separate reviewer contexts.
2. The researcher agent uses HITL (human-in-the-loop) after each batch of web searches to guide the search direction iteratively.
3. The writer agent operates in three phases: context loading → draft generation → evaluator-optimizer loop (3–4 review iterations).
4. Reviewer and writer maintain **strictly separate contexts** — the reviewer cannot access few-shot examples or writer system prompts.
5. Gemini 1.5 Pro handles grounded web search with citation extraction; Perplexity sonar-pro serves as fallback.
6. Model-switching is enabled by a unified `LLMClient` abstraction — supports both Anthropic Claude and Google Gemini without code changes.
7. All LLM calls are traced to `traces.jsonl`; cost and latency per step are logged to `metrics.jsonl`.
8. Evaluation dataset of 20 MDPI articles (13–20 pages) is used with an LLM judge iteratively refined on a dev split by F1 score.

## Narrative Arc
1. Open with the **personalisation gap** in current e-learning: one-size-fits-all content fails diverse learner populations.
2. Introduce multi-agent AI as the proposed solution — two specialised agents sharing structured context.
3. Walk through the methodology: data collection (web research), writing pipeline, review loop.
4. Present quantitative results: time savings, content quality scores (F1 judge ≥ 0.80), student outcome proxies.
5. Situate findings in literature; acknowledge limitations (API costs, latency).
6. Conclude with practical deployment recommendations and open research questions.

## Target Length
- **Minimum:** 15 pages (A4, two-column MDPI layout)
- **Expected:** 16–18 pages
- **Word count target:** 6000–8000 words

## Language Requirements
- Primary language: **English** (formal academic register)
- BiDi requirement: one chapter or subsection in **Hebrew** using polyglossia `\begin{hebrew}...\end{hebrew}`, followed by English translation.
- Abbreviations must be defined on first use (e.g., LLM, HITL, IMRAD, API, MCP).

## Required Visual Elements
| Element | Where | Content |
|---|---|---|
| Table 1 | Section 3 | Agent capability comparison (rows: Researcher, Writer, Reviewer; columns: Context, Tools, Output, Temperature) |
| Table 2 | Section 4 | Quantitative results (metric, baseline, proposed, improvement %) |
| Figure 1 | Section 1 or 3 | Multi-agent architecture diagram (TikZ or includegraphics) |
| Figure 2 | Section 4 | F1 score vs. iteration (line plot — PNG from `assets/graphs/generate_graph.py`) |
| Equation 1 | Section 3 | Weighted scoring formula: $S = 0.25C + 0.25A + 0.20T + 0.20R + 0.10Q$ |

## Cover Page Information
| Field | Value |
|---|---|
| Title | (as above) |
| Running Title | AI Agents for Adaptive Learning |
| Author 1 | Nagham Mnsor |
| Affiliation | Department of Computer Science, [Institution] |
| Correspondence | naghammnsor@gmail.com |
| Received / Revised / Accepted / Published | Leave blank (template placeholders) |
| License | CC BY 4.0 |
| DOI | 10.3390/[journal]-[volume]-[article] (placeholder) |

## Citation Style
Numbered in-text citations: [1], [2], [1,3], [4–6]
Reference list style (MDPI standard):
```
1. Author, A.; Author, B. Title of Article. Journal Year, Volume, Pages. https://doi.org/...
```

## Priority Hierarchy for Conflicts
1. Guideline requirements (this file) — highest
2. Research notes (`data/research.md`) — verified facts
3. Writing profiles (`profiles/*.md`) — style and structure conventions
