# Start Debate Command

Run a fully automated 5-round debate. You play all three roles in sequence.
Topic is fixed. No input needed. Run all 5 rounds in one response without stopping.

**TOPIC: "Is remote work better than working from the office?"**

---

## The Three Roles

**FATHER** — Neutral moderator. Validates JSON, detects agreement/repetition,
tracks context window, enforces timer, routes messages, declares winner.

**PRO** — Argues FOR remote work. Style: confident, data-driven.
Output: JSON with argument, evidence_url, rebuttal_reference, word_count.

**CON** — Argues AGAINST remote work. Style: skeptical, questioning.
Output: JSON with argument, evidence_url, rebuttal_reference, word_count.

---

## Round Format (repeat for rounds 1–5)

```
=== ROUND N/5 ===

[PRO responds — JSON output]

FATHER validates:
[Validation JSON — check all fields, word count, URL format]
[Agreement scan — show result]
[Repetition scan — show result]
[Route JSON — from: pro, to: con]
[CONTEXT] Round N: +<tokens> | Total: <WCn> tokens

[CON responds — JSON output]

FATHER validates:
[Validation JSON]
[Agreement scan — show result]
[Repetition scan — show result]
[Route JSON — from: con, to: pro]
[CONTEXT] Round N updated: +<tokens> | Total: <WCn> tokens

=================
```

---

## Round 1 Special Rule
PRO opens with their strongest argument. No opponent to rebut yet.
Set `rebuttal_reference` to `"opening argument"` for round 1 only.

---

## After Round 3 — Context Summarization
```
[CONTEXT] Summarizing rounds 1-2 to save tokens...
[CONTEXT] Summary: PRO argued X, Y. CON argued A, B. Tokens saved: ~<N>
[CONTEXT] New baseline: WC3 = <tokens>
```

---

## Timer Rule
If any response is missing required fields or implausibly incomplete, log:
```json
{"action": "timer_warning", "target": "<agent>", "round": <N>}
```
Two warnings for the same agent = skip that agent's turn for that round.

---

## After Round 5 — Verdict
Father scores both agents (0–25 per category × 4 categories = 100 max).
Output final verdict JSON with: pro_score, con_score, winner, reasoning,
total_interventions, total_tokens_used, rounds_completed.
Tie (50/50) is forbidden. Minimum split: 60/40.

---

## Start now. Do not stop between rounds. Do not ask questions. Run all 5 rounds.
