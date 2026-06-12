# PRD — Evaluator-Optimizer Loop
**Per-Mechanism Product Requirements**

| Field | Value |
|---|---|
| Version | 1.00 |
| Mechanism | Phase 3 Evaluation & Optimization Loop |
| Files | `src/article_writer/writing/evaluator.py`, `optimizer.py`, `loop_controller.py` |

## Scope
The evaluator-optimizer loop is Phase 3 of the writing pipeline. It scores the LaTeX draft on 5 weighted dimensions, produces structured critique, and iteratively revises the draft until quality threshold is met or max iterations is reached.

## Evaluation Rubric
| Dimension | Weight | Evaluation Criteria |
|---|---|---|
| Coverage | 25% | All key points from `guideline.md` addressed in the draft |
| Accuracy | 25% | Every factual claim backed by a `\cite{}` from `research.md` |
| Style | 20% | Writing matches `profiles/Characters.md` (formal, no first person, sentence length) |
| Structure | 20% | Document follows `profiles/Structure.md` (sections, TOC, cover, headers) |
| Citation Quality | 10% | Citations in IEEE format, no dead links, all `\cite{}` keys in `.bib` |

## Weighted Score Formula
```
weighted_score = coverage*0.25 + accuracy*0.25 + style*0.20 + structure*0.20 + citation_quality*0.10
```

## Critique Output Format
`results/critique_v{iteration}.md`:
```markdown
# Critique — Iteration 1
Weighted Score: 7.25/10

- [Coverage] Section 3 does not address key point "algorithmic bias" from guideline.md
- [Accuracy] Claim on page 4 "94% accuracy" has no citation
- [Style] Paragraph 2 of Section 1 uses first person ("I found that...")
- [Citation] \cite{topol2019} key missing from references.bib
```

## Loop Control
| Condition | Behavior |
|---|---|
| iteration < 2 | Always continue (minimum 2 iterations enforced) |
| iteration ≥ 2 AND weighted_score ≥ threshold (8.0) | Stop loop |
| iteration = max_iterations | Stop loop regardless of score |

## Draft Versioning
- Initial draft: `results/draft_v1.tex`
- After each optimization: `results/draft_v{N+1}.tex`
- Final draft: highest version number at loop exit

## Observability
- `results/eval_log.json` — appended after every evaluation with scores and timestamp
- `results/run_log.txt` — INFO log for each iteration start/end and score

## Acceptance Criteria
- AC-EO1: Evaluator returns EvaluationScore with all 5 dimension scores (1-10)
- AC-EO2: Weighted score computation matches the formula above
- AC-EO3: Minimum 2 iterations always execute
- AC-EO4: Critique file written to correct versioned path after each evaluation
- AC-EO5: eval_log.json has ≥ 1 entry per loop iteration
- AC-EO6: Optimizer saves revised draft to `draft_v{N+1}.tex`
- AC-EO7: Optimizer validates revised draft has `\begin{document}` and `\end{document}`
- AC-EO8: Human manager review always happens after loop (never bypassed)
