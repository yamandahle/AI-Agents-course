# Skills Summary — Article Writer System

All skills are stored under `skills/<name>/SKILL.md`. Each skill is injected into the relevant agent's backstory at initialization via `BaseAgentMixin._load_skills()`.

---

## Skills Table

| Name | File | Trigger | Agent | Purpose |
|---|---|---|---|---|
| `research-specialist` | `skills/research/SKILL.md` | Always injected | ResearcherAgent | Guides the researcher through search batches, citation extraction, content filtering, and research.md writing |
| `article-writer` | `skills/writing/SKILL.md` | Always injected | WriterAgent | Guides the writer through 3 phases: context load, draft generation, evaluator-optimizer loop |
| `catch-me-up` | `skills/catch-me-up/SKILL.md` | Phrase "catch me up" | All agents | Delivers a one-screen project status summary including directory tree, agents, tools, and next action |

---

## Skill Details

### research-specialist
**Purpose:** The ResearcherAgent reads this skill before every task. It specifies the exact tool-call sequence, output format for `research.md`, and 8 hard constraints (no hallucinated sources, no LOW confidence content, pause every 5 queries, etc.).

**Example use:** Agent calls `deep_research` with query "FDA approved AI medical devices 2024", then pipes result through `content_filter` with `"..content.. | Topic: AI in Healthcare"`.

**Constraints (summary):**
- Never keep LOW confidence content
- Minimum 10 cited facts before human review
- Every fact must have inline citation
- Max 5 queries per batch before human pause

---

### article-writer
**Purpose:** The WriterAgent reads this skill before every task. It specifies the 3-phase writing pipeline, all mandatory article elements (cover, TOC, BiDi chapter, formula, table, graph, image, bibliography), and LaTeX constraints.

**Example use:** After loading all profiles, agent generates `\begin{titlepage}...\end{titlepage}` cover, `\tableofcontents`, and `\begin{equation}...\end{equation}` formula as shown in the skill examples.

**Constraints (summary):**
- Never remove previously passing sections
- Never shrink below 15 pages
- Every claim must be `\cite{}`'d
- Output must compile with LuaLaTeX

---

### catch-me-up
**Purpose:** Any agent (or Claude Code assistant) reading this skill knows to respond with a structured one-screen project status when the user types "catch me up". This is particularly useful mid-session when the manager wants a quick reorientation.

**Example use:** User types "catch me up" → agent or assistant responds with: project name, current stage, next action, directory tree, agents list, tools list, and pipeline overview. All in ≤ 80 lines.

**Constraints (summary):**
- Trigger phrase is exactly "catch me up" (case-insensitive)
- Output ≤ 80 lines
- Always state current stage and next action
- Never modify files when triggered
