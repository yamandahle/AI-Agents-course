"""3–4 iteration review loop: Reviewer (isolated context) ↔ Editor (full context)."""
from __future__ import annotations

import json
from pathlib import Path

from article_writer.shared.llm_client import LLMClient
from article_writer.writing.reviewer import Reviewer, ArticleReview
from article_writer.writing.editor import Editor


class ReviewLoop:
    """Runs N review-edit cycles, saving every version to results/."""

    def __init__(
        self,
        iterations: int = 3,
        guideline_path: str | Path = "data/guideline.md",
        research_path: str | Path = "data/research.md",
        profiles_dir: str | Path = "profiles",
        few_shot_dir: str | Path = "few_shot_examples",
        results_dir: str | Path = "results",
        llm: LLMClient | None = None,
    ) -> None:
        self.iterations = max(2, min(iterations, 4))
        self.guideline = Path(guideline_path)
        self.research = Path(research_path)
        self.profiles = Path(profiles_dir)
        self.results = Path(results_dir)
        self.results.mkdir(parents=True, exist_ok=True)
        _llm = llm or LLMClient()
        self._reviewer = Reviewer(llm=_llm)
        self._editor = Editor(llm=_llm, few_shot_dir=few_shot_dir)

    def run(self, initial_draft: str | Path) -> Path:
        """Run the full review loop; returns path to draft_final.tex."""
        current = Path(initial_draft)
        review: ArticleReview | None = None
        for i in range(1, self.iterations + 1):
            review = self._reviewer.review(
                current,
                guideline_path=self.guideline,
                research_path=self.research,
                profiles_dir=self.profiles,
            )
            self._save_review(review, version=i)
            print(
                f"[review_loop] iteration {i}/{self.iterations} — "
                f"score={review.overall_score:.1f} {review.pass_fail} "
                f"({len(review.comments)} comments)"
            )
            if review.pass_fail == "PASS" and i >= 2:
                print(f"[review_loop] early stop at iteration {i}")
                break
            next_version = i + 1
            current = self._editor.apply(
                current, review,
                guideline_path=self.guideline,
                research_path=self.research,
                profiles_dir=self.profiles,
                version=next_version,
            )
        final = self.results / "draft_final.tex"
        final.write_text(current.read_text(encoding="utf-8"), encoding="utf-8")
        return final

    def _save_review(self, review: ArticleReview, version: int) -> None:
        out = self.results / f"review_v{version}.json"
        data = {
            "version": version,
            "overall_score": review.overall_score,
            "pass_fail": review.pass_fail,
            "comments": [c.model_dump() for c in review.comments],
        }
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
