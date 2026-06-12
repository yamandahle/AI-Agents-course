"""Reviewer agent — reads ONLY the draft; has no access to writer context or few-shots."""
from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel

from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.llm_client import LLMClient

_PROVIDER_TO_SERVICE = {"anthropic": "anthropic", "google": "gemini"}

_REVIEWER_SYSTEM = """\
You are an expert academic article reviewer for MDPI journals.
You receive ONLY the article draft, the submission guideline, research notes, and writing profiles.
You do NOT have access to few-shot examples, the writer's instructions, or internal system context.

Your task: identify the TOP 5 most critical violations, prioritised in this order:
  1. Coverage — page count, missing required sections, missing equation/figure/table
  2. Structure — section order, BiDi Hebrew paragraphs, titlepage, TOC
  3. Accuracy — factual errors, wrong statistics, incorrect claims vs research notes
  4. Terminology — wrong domain terms, inconsistent naming
  5. Characters — sentences over 25 words, paragraphs outside 4-7 sentence range

Select at most 5 comments total. Choose the highest-severity issues first.
For each issue output a JSON object with these exact keys:
  - "profile": which profile or constraint is violated
      (one of: "Structure", "Terminology", "Characters", "Coverage", "Accuracy", "Citation")
  - "location": where in the article (e.g. "Abstract, sentence 2", "Section 2.3, para 1")
  - "comment": what is wrong — keep it to 1-2 lines

Respond with ONLY a JSON object:
{
  "comments": [{"profile": "...", "location": "...", "comment": "..."}, ...],
  "overall_score": <float 0-10>,
  "pass_fail": "PASS" | "FAIL"
}
Do not include anything outside the JSON. The "comments" array must have at most 5 items.
"""


class ReviewComment(BaseModel):
    profile: str
    location: str
    comment: str


class ArticleReview(BaseModel):
    comments: list[ReviewComment]
    overall_score: float
    pass_fail: str


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


class Reviewer:
    """Scores a draft against guideline + research + profiles — NEVER sees writer context."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()
        self._gate = ApiGatekeeper()

    def review(
        self,
        draft_path: str | Path,
        guideline_path: str | Path = "data/guideline.md",
        research_path: str | Path = "data/research.md",
        profiles_dir: str | Path = "profiles",
    ) -> ArticleReview:
        draft = _load(Path(draft_path))
        guideline = _load(Path(guideline_path))
        research = _load(Path(research_path))
        profiles = self._load_profiles(Path(profiles_dir))
        user_msg = (
            f"## SUBMISSION GUIDELINE\n{guideline}\n\n"
            f"## RESEARCH NOTES\n{research}\n\n"
            f"## WRITING PROFILES\n{profiles}\n\n"
            f"## ARTICLE DRAFT TO REVIEW\n{draft}"
        )
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        service = _PROVIDER_TO_SERVICE.get(provider, provider)

        def _call():
            return self._llm.complete(
                system=_REVIEWER_SYSTEM,
                user=user_msg,
                step=f"review:{Path(draft_path).stem}",
                temperature=0.1,
                max_tokens=16384,
            )

        resp = self._gate.execute(service, _call)
        return self._parse(resp.text)

    def _load_profiles(self, profiles_dir: Path) -> str:
        parts: list[str] = []
        for md in sorted(profiles_dir.glob("*.md")):
            parts.append(f"### {md.stem}\n{md.read_text(encoding='utf-8')}")
        return "\n\n".join(parts)

    def _parse(self, raw: str) -> ArticleReview:
        import re as _re
        raw = raw.strip()
        # Strip markdown code fences
        m = _re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
        if m:
            raw = m.group(1).strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        try:
            data = json.loads(raw[start:end])
            return ArticleReview.model_validate(data)
        except Exception:
            # Truncated JSON — try to extract partial comments
            try:
                comments_match = _re.search(r'"comments"\s*:\s*(\[[\s\S]*?\})\s*[,\]]', raw)
                score_match = _re.search(r'"overall_score"\s*:\s*([\d.]+)', raw)
                pass_match = _re.search(r'"pass_fail"\s*:\s*"(\w+)"', raw)
                if score_match:
                    score = float(score_match.group(1))
                    pf = pass_match.group(1) if pass_match else "FAIL"
                    return ArticleReview(
                        comments=[ReviewComment(
                            profile="Parse",
                            location="whole article",
                            comment="Review partially parsed (truncated output).",
                        )],
                        overall_score=score,
                        pass_fail=pf,
                    )
            except Exception:
                pass
            return ArticleReview(
                comments=[ReviewComment(
                    profile="Parse",
                    location="whole article",
                    comment="Reviewer returned unparseable output.",
                )],
                overall_score=0.0,
                pass_fail="FAIL",
            )
