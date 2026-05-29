---
name: web_search
description: Performs targeted online searches to gather evidence and data. Use when an agent needs to back an argument with real-world statistics or check a fact.
---

# Web Search Skill

This skill enables agents to look up information externally to support their stances with up-to-date data and reduce hallucinations.

## How It Works

1.  **Query Generation**: Formulates a search query based on the current debate topic and the agent's specific stance.
2.  **Search Execution**: Uses a search engine to find relevant articles, papers, or news.
3.  **Data Extraction**: Scrapes the most relevant snippets or text from the top results.
4.  **Verification**: Compares search results with the agent's internal knowledge to ensure reliability.

## Workflow

- **Trigger**: "Search the web for...", "Find evidence for...", "What are the latest statistics on...".
- **Output**: Returns a list of facts or data points with their sources.
