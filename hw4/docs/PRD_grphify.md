---
title: PRD — Grphify Analysis Mechanism
version: "1.00"
status: draft
---

# PRD — Grphify Graph Analysis

## 1. Purpose

This document covers the Grphify scanning step: cloning the target repo, running Grphify, and
producing the graph artifacts that feed the CrewAI agents.

## 2. Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Target Python repo | `soarsmu/BugsInPy` → `thefuck` project | Read-only clone |
| Grphify CLI | pip-installed tool (via uv) | Scans via Python AST |

## 3. Outputs

| Output | Location | Format |
|--------|----------|--------|
| `graph.json` | `artifacts/graph.json` | JSON — nodes + edges |
| `index.md` | `artifacts/index.md` | Markdown index of all files |
| `hot.md` | `artifacts/hot.md` | Top-N hottest nodes by centrality |
| Obsidian vault | `obsidian/` | Markdown notes + backlinks |

## 4. Edge Types

| Type | Meaning | Confidence |
|------|---------|-----------|
| `Extracted` | Confirmed function call (from AST) | High |
| `Inferred` | LLM-inferred connection (from comments/text) | Medium |
| `Ambiguous` | Needs human review | Low |

## 5. Service: `GraphBuilderService`

Responsibilities:
1. Clone `thefuck` source into `data/thefuck/`
2. Run Grphify CLI on `data/thefuck/`
3. Move outputs to `artifacts/`
4. Parse `graph.json` and return a `Graph` dataclass
5. Generate Obsidian vault files in `obsidian/`

All external process calls go through the SDK. No subprocess calls in service layer directly.

## 6. Graph Metrics to Compute

After parsing `graph.json`, compute and store:
- Node count, edge count
- Top-10 nodes by degree (in + out)
- Number of communities (connected subgraphs)
- Bridges (edges whose removal disconnects the graph)

## 7. Success Criteria

- `graph.json` exists and is valid JSON
- At least 50 nodes present
- All 3 edge types represented
- `hot.md` contains top-10 nodes
- Obsidian vault opens without errors

## 8. Failure Modes

| Failure | Handling |
|---------|----------|
| Grphify CLI not found | Raise `ConfigError`, log, abort |
| Empty graph (< 10 nodes) | Raise `AnalysisError`, suggest different repo |
| Clone fails | Raise `DownloadError`, retry via Gatekeeper |
