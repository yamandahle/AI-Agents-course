# Stage 2 — How to Run the CLI Debate

## What This Stage Is
Stage 2 is semi-automatic. Claude CLI plays all three roles (Father, PRO, CON)
in a single session using saved commands. You just type one command and watch.

---

## Prerequisites
- Claude CLI installed and authenticated
- You are inside the hw2 folder when you open the terminal

---

## Step 1 — Open terminal in the hw2 folder

```
cd C:\Users\ASUS\Desktop\AI-Agents-course\hw2
claude
```

This opens Claude CLI with the hw2 folder as context, which means
Claude can see the `.claude/commands/` folder automatically.

---

## Step 2 — Run the debate

Type exactly this in the Claude CLI prompt:

```
/start_debate
```

Claude will:
1. Load the fixed topic (Remote Work vs Office Work)
2. Play PRO and make an opening argument with a cited web source
3. Play FATHER and route to CON, checking for agreement or repetition
4. Play CON and counter-argue with a cited web source
5. Play FATHER and check again, intervene if needed
6. Repeat for 5 rounds
7. Play FATHER and declare a winner with scores — no tie allowed

---

## Step 3 — What to watch for

While the debate runs, note:
- Does FATHER intervene at any point? When and why?
- Does PRO or CON slip and soften their position?
- Are the web sources real and relevant?
- Does the argument quality improve or decline across rounds?
- Does FATHER's verdict feel justified?

---

## Step 4 — Save the output

When the debate finishes:
- Copy the full debate output from the terminal
- Paste it into `stage2/debate_transcript.md`
- Take a screenshot of the Claude CLI session
- Save the screenshot to `assets/stage2/`

---

## Step 5 — Git commit

```
git add hw2/stage2/ hw2/assets/stage2/ hw2/.claude/
git commit -m "feat: Stage 2 CLI command debate"
git push origin yamandahle-hw2
```

---

## Individual Skill Commands (optional — for testing)

You can also test each skill separately before running the full debate:

```
/pro_skill The office enables mentorship and spontaneous collaboration that remote work cannot replicate.
```

```
/con_skill Remote workers show 13% higher productivity according to Stanford economist Nicholas Bloom.
```

```
/father_skill
```

These let you test each agent in isolation before the full automated run.
