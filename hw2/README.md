# HW2 — AI Debate System

**Course:** AI Agents
**Topic:** Is remote work better than working from the office?

---

## What This Project Does

This project builds an automated debate between two AI agents, supervised by a third.

- **PRO agent** argues that remote work is better
- **CON agent** argues that office work is better
- **Father agent** moderates — routes messages, detects when agents agree or repeat
  themselves, and at the end declares a winner with a score

The debate runs in 3 stages, each more automated than the last:
- **Stage 1** — fully manual (you copy-paste between two AI tools)
- **Stage 2** — semi-automatic (one Claude CLI command runs the full debate)
- **Stage 3** — fully automated Python code (coming next)

---

## Project Structure

```
hw2/
  .claude/
    commands/
      pro_skill.md        ← defines how PRO agent thinks and argues
      con_skill.md        ← defines how CON agent thinks and argues
      father_skill.md     ← defines how Father moderates and scores
      start_debate.md     ← main command: runs the full 5-round debate
  stage1/
    pro_prompt.md         ← prompt pasted into ChatGPT
    con_prompt.md         ← prompt pasted into Gemini
    HOW_TO_RUN.md         ← step-by-step manual instructions
    debate_transcript.md  ← full Stage 1 debate conversation
    observations.md       ← what we noticed and learned
  stage2/
    HOW_TO_RUN.md         ← how to run /start_debate in Claude CLI
  docs/
    PRD.md                ← full requirements and acceptance criteria
    PLAN.md               ← architecture, class diagram, IPC design
    TODO.md               ← all tasks across all phases
    PRD_father_agent.md   ← Father agent detailed spec
    PRD_debate_agents.md  ← PRO and CON agents detailed spec
    PRD_gatekeeper.md     ← API gatekeeper spec
    PRD_logger_watchdog.md ← logger and watchdog spec
  assets/
    stage1/               ← screenshots from Stage 1
    stage2/               ← screenshots from Stage 2
```

---

## Stage 1 — Manual Debate

### What it is
The simplest version. You open two browser tabs — ChatGPT for PRO, Gemini for CON.
You paste the debate prompt into each, then manually copy-paste arguments back and forth.
You act as the Father — you decide who won at the end.

### How to run it
1. Open `stage1/pro_prompt.md` — paste its contents into a new ChatGPT conversation
2. Open `stage1/con_prompt.md` — paste its contents into a new Gemini conversation
3. Follow the steps in `stage1/HOW_TO_RUN.md`
4. Run 5 rounds, then write your verdict in `stage1/observations.md`

### What we learned
Both agents stayed in character and never agreed with each other.
By round 3, both started repeating the same arguments.
CON was more persuasive (8/10 vs 6/10) because it used more specific numbers.
Neither agent provided real URLs — only study names. This was fixed in Stage 2.

Full transcript → [`stage1/debate_transcript.md`](stage1/debate_transcript.md)

---

## Stage 2 — Claude CLI Command

### What it is
All three agents (PRO, CON, Father) run inside a single Claude CLI session.
You type one command and the full 5-round debate runs automatically.

Each agent is defined as a saved Claude CLI command (a `.md` file in `.claude/commands/`).
When you type `/start_debate`, Claude loads the command and plays all three roles in sequence.

### What Father does in every round
1. Receives the agent's response as structured JSON
2. Validates the JSON — checks all required fields and word count (max 50 words)
3. Verifies the `evidence_url` is a real link using web search
4. Checks the agent actually responded to the opponent — not just stated a new fact
5. Scans for agreement phrases ("good point", "fair enough", etc.) → intervenes if found
6. Checks if the agent repeated a previous argument → intervenes if found
7. Tracks total tokens: `WCn = WCn-1 + tokens(PRO) + tokens(CON)`
8. Routes to the next agent

### JSON format every agent uses
```json
{
  "round": 1,
  "sender": "pro",
  "argument": "Your point is wrong because...",
  "evidence_url": "https://example.com/real-study",
  "rebuttal_reference": "exact words from opponent that you are responding to",
  "word_count": 47
}
```

### How to run it
```bash
# Step 1 — open a terminal and go to the hw2 folder
cd "C:\Users\ASUS\Desktop\AI-Agents-course\hw2"

# Step 2 — open Claude CLI
claude

# Step 3 — run the debate
/start_debate
```

The debate runs automatically. After 5 rounds, Father outputs a verdict JSON:
```json
{
  "verdict": {
    "pro_score": 72,
    "con_score": 58,
    "winner": "pro",
    "reasoning": "PRO consistently responded to CON's claims directly...",
    "total_interventions": 1,
    "total_tokens_used": 1840,
    "rounds_completed": 5
  }
}
```
A tie (50/50) is forbidden. The minimum split is 60/40.

Screenshots → [`assets/stage2/`](assets/stage2/)

---

## Stage 3 — Full Python (coming next)

Full automation with Python classes, an API Gatekeeper, Watchdog process monitor,
structured rotating logs, and a terminal menu. No manual steps required.

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| All messages go through Father only | Prevents direct agent communication — enforces rules |
| Agents respond to opponent first | Ensures real debate, not two parallel speeches |
| URLs verified by Father via web search | Prevents agents from fabricating citations |
| JSON format for all messages | Structured, easy to validate, saves tokens |
| Interventions ≠ validation checks | Keeps the intervention count honest and meaningful |
