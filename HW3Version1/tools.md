# Tools Summary — Article Writer System

All tools are implemented under `src/article_writer/tools/`. Each tool inherits from `ArticleBaseTool` which inherits from `crewai.tools.BaseTool`. All tools route their API calls through the `ApiGatekeeper`.

---

## Tools Table

| Name | File | Agent | API Backend | Query Parameter |
|---|---|---|---|---|
| `deep_research` | `tools/deep_research_tool.py` | ResearcherAgent | Gemini 1.5 Pro (fallback: Perplexity sonar-pro) | `prompt` (research query string) |
| `researcher_handler` | `tools/researcher_handler.py` | ResearcherAgent | Anthropic Claude Haiku (session management) | `prompt` (current research intent) |
| `citation_extractor` | `tools/citation_extractor.py` | ResearcherAgent | Anthropic Claude Haiku | `prompt` (URL or raw text passage) |
| `content_filter` | `tools/content_filter.py` | ResearcherAgent | Anthropic Claude Haiku | `prompt` ("content | Topic: topic string") |

---

## Tool Details

### deep_research

**Description:** The primary web search tool. Calls Gemini 1.5 Pro with Google Search grounding enabled to retrieve factual answers with citations. Falls back to Perplexity sonar-pro if Gemini fails or returns LOW confidence.

**Input schema:**
```json
{
  "prompt": "<research query as plain text>"
}
```

**Output format:**
```
## Answer
{factual answer paragraph}

## Citations
- [Title of Source](https://url.com) — Author, Date
- [Second Source](https://url2.com) — Author, Date

**Confidence:** HIGH
```

**Prompt templates:**

*Gemini system prompt:*
```
You are a research assistant. Answer the following query with factual, cited information.
Use only verifiable sources. Include the URL for every source you cite.
Query: {prompt}
```

*Perplexity fallback message:*
```
{prompt}

Please provide a comprehensive, factual answer with citations to credible sources.
```

**Error handling:** If both Gemini and Perplexity fail, return empty string and log a WARNING. Do not raise — allow the researcher_handler to suggest an alternative query.

---

### researcher_handler

**Description:** Session manager for the research process. Tracks which URLs have been visited and which queries have been run. Suggests new queries that avoid repetition. Increments batch counter so the agent knows when to pause for human feedback.

**Input schema:**
```json
{
  "prompt": "<current research intent — what the agent is trying to find out>"
}
```

**Output format:**
```json
{
  "batch": 2,
  "new_queries": [
    "AI healthcare bias racial disparity clinical studies",
    "algorithm accountability healthcare regulation EU AI Act",
    "patient data privacy HIPAA AI training violations"
  ],
  "summary_so_far": "Covered: FDA approvals, accuracy statistics, cost reduction. Not yet covered: ethics, legal frameworks, patient safety."
}
```

**Prompt template:**
```
You are a research session manager. The researcher's current intent is: "{prompt}".

Previously executed queries:
{previous_queries}

Already visited URLs:
{visited_urls}

Generate exactly 3 new search queries that:
1. Are directly relevant to the research intent
2. Have NOT been searched before (avoid duplicates)
3. Cover angles not yet explored

Return JSON only: {"new_queries": [...], "summary_so_far": "..."}
```

**Error handling:** If LLM returns malformed JSON, fall back to generating 3 simple variations of the original prompt string.

---

### citation_extractor

**Description:** Formats a citation from a URL or raw text passage into a consistent markdown link format. Detects whether input is a URL or text, calls the appropriate extraction logic, and returns a formatted citation string.

**Input schema:**
```json
{
  "prompt": "<URL string> OR <raw text passage containing publication information>"
}
```

**Output format:**
```
[Title of the Publication](https://url.com) — Author Name, YYYY-MM-DD
```

**Prompt templates:**

*URL extraction prompt:*
```
Extract citation metadata from this URL: {prompt}

Return JSON only:
{"title": "...", "author": "...", "date": "YYYY-MM-DD", "url": "{prompt}"}

If a field is unknown, use "Unknown".
```

*Text extraction prompt:*
```
Extract citation information from this text passage: "{prompt}"

Return JSON only:
{"title": "...", "author": "...", "date": "YYYY-MM-DD", "publication": "..."}

If a field is unknown, use "Unknown".
```

**Error handling:** If URL is malformed or inaccessible, return a plain-text citation: `{prompt} (source unverified)`. Never crash — a degraded citation is better than no citation.

---

### content_filter

**Description:** LLM-based relevance and trustworthiness scorer. Takes a content chunk and topic, scores the content on relevance (0–100) and trustworthiness (0–100), and classifies it as HIGH (≥80), MEDIUM (50–79), or LOW (<50). LOW content is automatically discarded.

**Input schema:**
```json
{
  "prompt": "<content chunk> | Topic: <article topic>"
}
```

**Output format:**
```
KEEP:HIGH:Content is from a peer-reviewed journal directly relevant to the topic.
```
or:
```
DISCARD:LOw is from a personal blog with no citations and contradicts peer-reviewed sources.
```

**Prompt template:**
```
You are a fact-checker and relevance scorer for academic research.

Topic: {topic}
Content to evaluate: {content}

Score this content on two dimensions (0-100 each):
1. Relevance: How directly does this content address the topic?
2. Trustworthiness: Is this from a credible source (peer-reviewed, official, expert)?

Classify as:
- HIGH: both scores ≥ 80
- MEDIUM: both scores ≥ 50 (or one ≥ 80 and other ≥ 40)
- LOW: either score < 50

Return JSON only:
{"keep": true/false, "confidence": "HIGH"|"MEDIUM"|"LOW", "reason": "one sentence explanation"}
```

**Error handling:** If LLM returns malformed JSON, default to `keep=False, confidence=LOW, reason="Parse error — defaulting to discard for safety"`. Always fail safe (discard rather than include questionable content).
