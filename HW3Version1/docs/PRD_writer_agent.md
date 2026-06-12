# PRD — Writer Agent
**Per-Mechanism Product Requirements**

| Field | Value |
|---|---|
| Version | 1.00 |
| Mechanism | WriterAgent + EvaluatorAgent |
| Files | `src/article_writer/agents/writer_agent.py`, `writing/*.py` |

## Scope
The WriterAgent produces the LaTeX article through a 3-phase pipeline: context loading, draft generation, and evaluator-optimizer loop. The EvaluatorAgent is a sub-agent delegated by the Writer to score drafts.

## Inputs (Phase 1 — Context Load)
| File | Type | Role |
|---|---|---|
| `data/guideline.md` | Dynamic | WHAT to write |
| `data/research.md` | Dynamic | WHAT facts to use |
| `profiles/Structure.md` | Static | HOW: document structure |
| `profiles/Terminology.md` | Static | HOW: vocabulary rules |
| `profiles/Characters.md` | Static | HOW: voice and tone |
| `few_shot_examples/*.md` | Static | WHAT good output looks like |

## Phase 2 — Draft Generation
- DraftGenerator combines all context and calls LLM (Claude Sonnet)
- System prompt: all 3 writing profiles + LaTeX requirements
- Output validated: must contain `\begin{document}`, `\end{document}`, `\maketitle`, `\tableofcontents`
- Saved to: `results/draft_v1.tex`

## Phase 3 — Evaluator-Optimizer Loop
### Evaluator Rubric
| Dimension | Weight | What is measured |
|---|---|---|
| Coverage | 25% | All guideline key points addressed |
| Accuracy | 25% | All claims backed by research.md citations |
| Style | 20% | Matches Characters.md |
| Structure | 20% | Follows Structure.md |
| Citation Quality | 10% | IEEE format, valid URLs |

### Loop Control
- Minimum 2 iterations always enforced
- Stop condition: iteration ≥ 2 AND weighted_score ≥ 8.0
- Hard stop: max_iterations (default: 3)
- After loop: human manager does final review

## Output
- `results/article_final.tex` — polished LaTeX source
- `results/article_final.pdf` — compiled PDF (lualatex, ≥15 pages)
- `results/eval_log.json` — scores per iteration
- `results/critique_v{n}.md` — critique per iteration

## Acceptance Criteria
- AC-W1: Phase 1 loads all 6 input sources
- AC-W2: Draft passes LaTeX structural validation
- AC-W3: Evaluator-optimizer loop runs ≥ 2 iterations
- AC-W4: Final PDF is ≥ 15 pages
- AC-W5: PDF contains all mandatory elements (image, graph, table, formula, BiDi, bibliography)
- AC-W6: eval_log.json has ≥ 2 entries
