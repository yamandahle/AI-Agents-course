# PRD — MCP Tools
**Per-Mechanism Product Requirements**

| Field | Value |
|---|---|
| Version | 1.00 |
| Mechanism | 4 MCP-backed CrewAI Tools |
| Files | `src/article_writer/tools/*.py`, `src/article_writer/mcp/*.py` |

## Architecture
All tools inherit from `ArticleBaseTool(BaseTool)`. All external API calls route through `ApiGatekeeper`. The MCP server (`mcp_server.py`) exposes the same tools over the MCP stdio protocol for independent use.

## Tool 1: deep_research
| Field | Value |
|---|---|
| Input | `prompt`: research query string |
| Primary backend | Gemini 1.5 Pro (grounded search) |
| Fallback | Perplexity sonar-pro |
| Output | `## Answer\n...\n## Citations\n- [title](url)\n**Confidence:** HIGH/MEDIUM` |
| Error behavior | Return empty string on both backends failing |
| Prompt template | `"Search for: {prompt}. Provide factual answer with citations."` |

## Tool 2: researcher_handler
| Field | Value |
|---|---|
| Input | `prompt`: current research intent |
| Backend | Claude Haiku (session management LLM) |
| State | Per-session: visited_urls (set), previous_queries (list), batch_count (int) |
| Output | JSON: `{"batch": N, "new_queries": [...], "summary_so_far": "..."}` |
| Error behavior | Return 3 simple query variations as fallback |
| Prompt template | `"Given intent: {prompt}. Previously searched: {previous_queries}. Suggest 3 new angles."` |

## Tool 3: citation_extractor
| Field | Value |
|---|---|
| Input | `prompt`: URL string OR raw text passage |
| Backend | Claude Haiku |
| Detection | Input starting with "http" treated as URL; otherwise as text |
| Output | `[Title](url) — Author, YYYY-MM-DD` |
| Error behavior | Return `{prompt} (source unverified)` on failure |
| URL prompt | `"Extract citation metadata from URL: {prompt}. Return JSON: {title, author, date, url}"` |
| Text prompt | `"Extract citation from passage: {prompt}. Return JSON: {title, author, date, publication}"` |

## Tool 4: content_filter
| Field | Value |
|---|---|
| Input | `prompt`: `"content chunk | Topic: topic string"` |
| Backend | Claude Haiku |
| Classification | HIGH: both scores ≥80; MEDIUM: both ≥50; LOW: either <50 |
| Output | `KEEP:HIGH:reason` or `DISCARD:LOW:reason` |
| Error behavior | Default to `DISCARD:LOW:Parse error` for safety |
| Prompt template | `"Rate content for relevance to '{topic}' and trustworthiness. Return JSON: {keep, confidence, reason}"` |

## MCP Server
- Server name: `article-writer-research-server`
- Transport: stdio
- All 4 tools registered with `"prompt"` as required input field
- Dispatches to same tool classes as CrewAI tools

## Acceptance Criteria
- AC-T1: All 4 tools sanitize input before processing
- AC-T2: All tools log call via `_log_call()` at entry
- AC-T3: deep_research falls back to Perplexity on Gemini failure
- AC-T4: content_filter defaults to DISCARD on JSON parse error
- AC-T5: MCP server registers all 4 tools with correct schemas
- AC-T6: No direct API calls — all through ApiGatekeeper
