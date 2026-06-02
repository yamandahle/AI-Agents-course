# PRD — Father Agent (Judge / Moderator)

## Role
The Father is the sole orchestrator. It receives arguments from children,
decides whether to pass them on or intervene, and ultimately declares a winner.
It exists to enforce debate integrity — not to participate in the debate itself.

---

## Inputs

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| Child argument | DebateMessage | Pro or Con queue | Argument with round, content, sources, word_count |
| Round counter | int | Internal state | Tracks how many exchanges have occurred |
| Config | dict | ConfigManager | Word limit, round limit, intervention threshold |
| Debate history | list[DebateMessage] | Internal state | All prior messages for alignment detection |

---

## Outputs

| Output | Type | Destination | Description |
|--------|------|-------------|-------------|
| Routed message | DebateMessage | Opponent queue | Passes argument to the other child, possibly with note |
| Intervention | DebateMessage | Current child | Forces agent to re-argue from a new angle |
| Verdict | DebateMessage (type=verdict) | Logs + CLI | Winner, scores, justification — NO TIE |

---

## Constraints
- Must NEVER participate as a debater — Father's content is routing instructions only
- Must NEVER produce a tie — a 50/50 score is forbidden; 7/5 minimum split required
- Must detect alignment within 2 consecutive rounds of overlap and intervene
- Must enforce word count: reject and request rewrite if content exceeds limit
- Must track novelty: flag if child repeats the same point as a previous round
- Judges on persuasion structure (citation quality, opponent reference, argument novelty)
  NOT on factual correctness of claims

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Father participates in debate | Would bias the scoring; Father must be neutral arbiter |
| Father scores each round immediately | Creates premature anchoring; better to score holistically at the end |
| Tie allowed with explanation | Assignment explicitly forbids it — teaches decisive AI judgment |
| Father knows the debate topic | Unnecessary — rules-based judgment works without domain knowledge |

---

## Success Criteria
- Detects alignment (>50% semantic overlap) within 2 rounds and sends intervention
- Produces a verdict with two distinct numerical scores (e.g., 7 and 5 — never equal)
- Justification references at least 3 specific rounds by number
- Full 10-round debate completes without Father needing human input
- Intervention messages are logged separately from routing messages

---

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Both agents make identical arguments | Father intervenes with forced reframe prompt |
| Child exceeds word count | Father rejects, sends back with exact word limit reminder |
| Child fails to cite a source | Father flags and requests resubmission with citation |
| Child tries to concede or agree | Father treats as alignment, sends mandatory disagreement instruction |
| Round count reaches 10 with no clear winner | Father chooses winner based on best-performing 3 rounds |
| Child process dies | Watchdog restarts; Father resumes from last known round |
