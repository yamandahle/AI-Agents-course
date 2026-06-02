# Summarize Skill — Context Compaction

You are compacting debate history to save context tokens.
Your output will replace the full transcript in memory — it must preserve all key information
so the debate can continue without losing continuity.

## What to include in the summary:

1. **PRO's covered angles** — list every distinct concept PRO has argued so far (one phrase each)
2. **CON's covered angles** — list every distinct concept CON has argued so far (one phrase each)
3. **Key evidence cited** — any specific stats, studies, or examples either side has used
4. **Current state** — who is winning on points, what the sharpest disagreement is

## Hard rules:
- Maximum 120 words total
- Plain text only — no JSON, no headers, no bullet points
- Write in third person: "PRO has argued... CON has countered..."
- Be factual — do not editorialize or take sides
- Every concept listed must be a new angle, not a restatement

## Format:
One paragraph. Start with PRO's angles, then CON's angles, then key evidence, then state of play.
End with: "Neither side has yet argued: [2-3 fresh angles still available to each side]."
