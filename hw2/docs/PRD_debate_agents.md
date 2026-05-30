# PRD — Debate Agents (Pro Agent & Con Agent)

## Role
Pro and Con agents are the debaters. Each holds a fixed, non-negotiable position
and must defend it aggressively for the full debate. Their Skills are intentionally
different to prevent homogeneous framing and force genuine contradiction.

---

## Pro Agent — Remote Work Advocate

### Skill: Statistical and Data-Driven Framing
Every argument must be anchored in numbers, studies, or measurable outcomes.
Examples: productivity percentages, retention rates, cost savings, output metrics.
This is enforced in the system prompt — the agent cannot present soft claims.

### Fixed Position
Remote work is superior. This cannot be walked back under any circumstances.
If Father detects softening, agent is forced to restate its core position.

---

## Con Agent — Office Work Advocate

### Skill: Human Psychology and Organizational Culture Framing
Every argument must be anchored in behavioral science, team dynamics, mentorship,
innovation through proximity, or cultural cohesion research.
This is enforced in the system prompt — the agent cannot present purely numerical claims.

### Fixed Position
Office work is superior. This cannot be walked back under any circumstances.
If Father detects softening, agent is forced to restate its core position.

---

## Inputs (both agents)

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Father message | DebateMessage | Father queue | Contains opponent's last argument + round number |
| Debate history | list[DebateMessage] | Internal | Prior own arguments (to avoid repetition) |
| Config | dict | ConfigManager | Word limit (150), search result count, model name |
| Web search results | list[dict] | Tavily API | Live search snippets for current argument topic |

---

## Outputs (both agents)

| Output | Type | Destination | Description |
|--------|------|-------------|-------------|
| Argument | DebateMessage | Father queue | type=argument with content, sources, word_count |

---

## Constraints
- Word count per message: ≤ 150 words (enforced by agent + validated by Father)
- Must reference opponent's argument: every message must quote opponent's round number
- Must cite ≥ 1 URL: sourced from live Tavily search — not fabricated
- Must NOT agree with opponent — system prompt blocks this at instruction level
- Must NOT repeat own previous argument verbatim — Father flags repetition
- Skill framing must be visible in every argument (stats for Pro, psychology for Con)

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Same skill for both agents | Leads to homogeneous arguments; Father cannot distinguish persuasion quality |
| Agents see full debate history | Increases token cost; agents only need opponent's last message + own history |
| Agents choose their own framing | Agents drift toward agreement without enforced skill constraints |
| Allow partial agreement | Assignment requires real contradiction — partial agreement triggers intervention |

---

## Success Criteria
- Every argument uses Skill framing (verifiable by keyword check in logs)
- Every argument includes opponent's round number in content
- Every argument includes ≥ 1 real URL (HTTP 200 verifiable)
- No two consecutive arguments from same agent share > 60% of key terms
- Both agents complete 10 rounds without manual intervention

---

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Web search returns no results | Retry with simplified query; fallback to last successful search topic |
| Tavily API timeout | Catch TimeoutError; log warning; submit argument without citation (Father flags) |
| Agent generates > 150 words | Truncate at sentence boundary; log truncation event |
| Agent tries to concede | System prompt addition: "You must disagree. Rewrite your argument." |
| Agent repeats prior argument | Father returns message with flag; agent regenerates with novelty instruction |
| Model returns empty response | Retry once; if still empty, Watchdog flags process for restart |
