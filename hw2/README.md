# HW2 — AI Debate System
**Course:** AI Agents | **Topic:** Remote Work vs Office Work

Three agents debate: PRO (remote work), CON (office work), and FATHER (judge).
Father routes all messages, detects agreement and repetition, and declares a winner.

---

## Project Structure

```
hw2/
  .claude/commands/     ← Claude CLI slash commands (Stage 2)
  stage1/               ← Manual debate prompts and transcript
  stage2/               ← CLI debate instructions and transcript
  docs/                 ← PRD, PLAN, TODO, component docs
  assets/               ← Screenshots from each stage
```

---

## Stage 1 — Manual Debate (ChatGPT vs Gemini)

Two separate AI tools were used manually — ChatGPT as PRO, Gemini as CON.
The human (Father) copy-pasted arguments between them for 5 rounds.

**What we learned:** Both agents drifted toward repeating the same 2-3 points
by round 3. Neither tried to agree. CON won (8/10 vs 6/10) because it used
more specific statistics that were harder to dismiss.

Full transcript: [`stage1/debate_transcript.md`](stage1/debate_transcript.md)
Observations: [`stage1/observations.md`](stage1/observations.md)

---

## Stage 2 — Claude CLI Command (`/start_debate`)

All three roles (PRO, CON, FATHER) run inside a single Claude CLI session.
Typing `/start_debate` runs the full 5-round debate automatically.

### How the commands work

| Command | Role | File |
|---------|------|------|
| `/start_debate` | Runs the full debate | `.claude/commands/start_debate.md` |
| `/pro_skill` | PRO agent behavior | `.claude/commands/pro_skill.md` |
| `/con_skill` | CON agent behavior | `.claude/commands/con_skill.md` |
| `/father_skill` | Father moderator rules | `.claude/commands/father_skill.md` |

### What Father does each round
1. Validates JSON response (fields, word count ≤ 50)
2. Verifies `evidence_url` is a real URL via web search
3. Checks the agent responded to the opponent — not just stated a new fact
4. Scans for agreement phrases → intervention if found
5. Checks for repeated arguments → intervention if found
6. Tracks context window: `WCn = WCn-1 + tokens(PRO) + tokens(CON)`
7. Routes to the next agent

Interventions are counted only for agreement and repetition — not for validation checks.

### Prompts Used to Build Stage 2

**Step 1 — Basic command structure:**
> Create 4 commands: `pro_skill.md` (argues FOR remote work, confident style, web search,
> under 150 words, starts with "PRO:"), `con_skill.md` (argues AGAINST, skeptical style,
> different from PRO), `father_skill.md` (neutral, routes messages, detects agreement and
> repetition, stops at 5 rounds, declares winner — no tie), `start_debate.md` (runs everything
> with `=== ROUND N/5 ===` format automatically).

**Step 2 — Technical additions:**
> JSON format for every response (argument, evidence_url, rebuttal_reference, word_count).
> Context window tracking using `WCn = WCn-1 + PRO + CON`, summarize after round 3.
> 30-second timer per agent. Father validates JSON before accepting. Agreement and repetition
> detection from JSON. Final verdict in JSON with scores, reasoning, total interventions,
> total tokens used.

**Step 3 — Quality fixes applied:**
> - Word limit reduced from 150 → 50 words
> - Father verifies `evidence_url` is real via web search before accepting
> - Agents must respond to opponent first — URL is support, not the main point
> - Conversational tone enforced — two people talking, not academic papers
> - Intervention counter fixed — only counts agreement and repetition, not validation checks

### Screenshots
See [`assets/stage2/`](assets/stage2/) for full session screenshots.

---

## Stage 3 — Full Python (coming next)

Full automation with OOP classes, Gatekeeper, Watchdog, structured logs, and CLI menu.

---

## How to Run Stage 2

```bash
cd hw2
claude
/start_debate
```
