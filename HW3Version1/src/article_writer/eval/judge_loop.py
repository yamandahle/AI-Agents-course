"""Iterative judge improvement loop: run on dev → compute F1 → refine → repeat."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from article_writer.shared.llm_client import LLMClient
from article_writer.eval.judge import ArticleJudge, JudgeResult, _DEFAULT_PROMPT as _JUDGE_DEFAULT_PROMPT
from article_writer.eval.f1_metrics import compute_f1, format_report, F1Result

_PROMPT_REFINER_SYSTEM = """\
You are improving an LLM judge prompt that evaluates academic article quality.
The judge currently achieves the F1 score shown. Identify what is causing errors
(false positives and false negatives) and output an improved judge system prompt.
Keep the same JSON output schema but adjust instructions to fix the identified errors.
Return ONLY the improved prompt text — nothing else.
"""

_F1_TARGET = 0.80
_MAX_ITERS = 5


@dataclass
class LoopIteration:
    iteration: int
    f1: F1Result
    prompt_used: str
    predictions: list[str]


class JudgeLoop:
    """Iterate judge prompt until F1 ≥ target on dev split or max iterations reached."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        f1_target: float = _F1_TARGET,
        max_iterations: int = _MAX_ITERS,
        guideline_path: str | Path = "data/guideline.md",
        research_path: str | Path = "data/research.md",
    ) -> None:
        self._llm = llm or LLMClient()
        self.f1_target = f1_target
        self.max_iterations = max_iterations
        gp = Path(guideline_path)
        rp = Path(research_path) if research_path else None
        self.guideline = gp.read_text(encoding="utf-8") if gp.exists() else ""
        self.research = rp.read_text(encoding="utf-8") if (rp and rp.exists() and rp.is_file()) else ""

    def run(
        self,
        dev_samples: list[dict],
        test_samples: list[dict],
        initial_prompt: str | None = None,
    ) -> dict:
        history: list[LoopIteration] = []
        current_prompt = initial_prompt or _JUDGE_DEFAULT_PROMPT
        judge = ArticleJudge(llm=self._llm, prompt=current_prompt)

        for i in range(1, self.max_iterations + 1):
            preds, labels = self._evaluate_split(judge, dev_samples)
            f1 = compute_f1(preds, labels)
            print(f"[judge_loop] iter {i}: {format_report(f1, 'dev')}")
            history.append(LoopIteration(iteration=i, f1=f1,
                                         prompt_used=current_prompt, predictions=preds))
            if f1.f1 >= self.f1_target:
                print(f"[judge_loop] converged at iteration {i} (F1={f1.f1:.4f})")
                break
            if i < self.max_iterations:
                current_prompt = self._refine_prompt(current_prompt, f1, dev_samples, preds, labels)
                judge = ArticleJudge(llm=self._llm, prompt=current_prompt)

        test_preds, test_labels = self._evaluate_split(judge, test_samples)
        test_f1 = compute_f1(test_preds, test_labels)
        print(f"[judge_loop] FINAL TEST: {format_report(test_f1, 'test')}")
        return {
            "iterations": len(history),
            "dev_f1_history": [h.f1.f1 for h in history],
            "test_f1": test_f1.f1,
            "final_prompt": current_prompt,
            "test_report": format_report(test_f1, "test"),
        }

    def _evaluate_split(
        self, judge: ArticleJudge, samples: list[dict]
    ) -> tuple[list[str], list[str]]:
        preds: list[str] = []
        labels: list[str] = []
        for s in samples:
            result = judge.judge(
                article_text=s.get("full_text", ""),
                guideline=self.guideline,
                research=self.research,
                article_id=s.get("article_id", ""),
            )
            preds.append(result.verdict)
            labels.append(s.get("label", "FAIL"))
        return preds, labels

    def _refine_prompt(
        self,
        current: str,
        f1: F1Result,
        samples: list[dict],
        preds: list[str],
        labels: list[str],
    ) -> str:
        errors = self._describe_errors(samples, preds, labels)
        user = (
            f"CURRENT JUDGE PROMPT:\n{current}\n\n"
            f"DEV F1: {f1.f1:.4f} (P={f1.precision:.4f}, R={f1.recall:.4f})\n"
            f"FP={f1.fp}, FN={f1.fn}\n\nERROR EXAMPLES:\n{errors}"
        )
        resp = self._llm.complete(
            system=_PROMPT_REFINER_SYSTEM, user=user,
            step="judge_prompt_refine", temperature=0.4,
        )
        return resp.text.strip()

    def _describe_errors(self, samples: list[dict], preds: list[str], labels: list[str]) -> str:
        lines: list[str] = []
        for s, p, g in zip(samples, preds, labels):
            if p.upper() != g.upper():
                error_type = "FP" if p.upper() == "PASS" else "FN"
                snippet = s.get("abstract", "")[:200]
                lines.append(f"[{error_type}] {s.get('article_id','')} — predicted={p} actual={g}\n  {snippet}")
        return "\n".join(lines[:5])
