"""LLM-based judge for evaluating article quality against guideline + research."""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from article_writer.shared.llm_client import LLMClient

_TRAINED_RESULTS_PATH = Path("eval_dataset/judge_results.json")


def load_trained_prompt(results_path: str | Path = _TRAINED_RESULTS_PATH) -> str | None:
    """Return the final refined prompt from a completed judge loop run, or None."""
    p = Path(results_path)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("final_prompt") or None
    except Exception:
        return None

_DEFAULT_PROMPT = """\
You are a strict academic journal editor for MDPI journals evaluating a submitted article.

PASS criteria (ALL must hold):
- Follows IMRAD structure: Introduction, Methods/Materials, Results, Discussion, Conclusions
- Abstract ≤300 words, contains objective, methods, key result, and conclusion sentences
- ≥15 numbered citations in correct MDPI format
- Every major claim has an inline citation [N]
- Keywords section present (5-10 terms)
- At least one table, one figure, or one equation
- Formal academic English; no first-person narrative

FAIL criteria (ANY one is sufficient):
- Missing any major IMRAD section
- Fewer than 10 citations
- Claims made without supporting citations
- Abstract missing or under 50 words
- No keywords
- Informal language or heavy use of "I/we found/we believe"
- Copied verbatim text from sources without quotation marks

Given:
1. The submission guideline (what the article must cover)
2. The research notes (verified facts the article must draw from)
3. The article text

Evaluate and respond ONLY with this JSON:
{
  "verdict": "PASS" | "FAIL",
  "confidence": <float 0.0-1.0>,
  "critique": "<exactly 3 sentences explaining verdict>",
  "dimension_scores": {
    "coverage": <int 1-10>,
    "accuracy": <int 1-10>,
    "structure": <int 1-10>,
    "style": <int 1-10>,
    "citations": <int 1-10>
  }
}
"""


class JudgeResult(BaseModel):
    verdict: str
    confidence: float
    critique: str
    dimension_scores: dict[str, int]
    article_id: str = ""


class ArticleJudge:
    """LLM judge that scores an article against guideline and research notes."""

    def __init__(self, llm: LLMClient | None = None, prompt: str | None = None) -> None:
        self._llm = llm or LLMClient()
        self.prompt = prompt or load_trained_prompt() or _DEFAULT_PROMPT

    def judge(
        self,
        article_text: str,
        guideline: str,
        research: str,
        article_id: str = "",
    ) -> JudgeResult:
        user = (
            f"## SUBMISSION GUIDELINE\n{guideline}\n\n"
            f"## RESEARCH NOTES\n{research}\n\n"
            f"## ARTICLE TO EVALUATE\n{article_text[:6000]}"
        )
        resp = self._llm.complete(
            system=self.prompt, user=user,
            step=f"judge:{article_id or 'unknown'}", temperature=0.1,
        )
        return self._parse(resp.text, article_id)

    def judge_from_paths(
        self,
        article_path: str | Path,
        guideline_path: str | Path = "data/guideline.md",
        research_path: str | Path = "data/research.md",
    ) -> JudgeResult:
        def read(p: str | Path) -> str:
            pp = Path(p)
            return pp.read_text(encoding="utf-8") if pp.exists() else ""
        return self.judge(
            article_text=read(article_path),
            guideline=read(guideline_path),
            research=read(research_path),
            article_id=Path(article_path).stem,
        )

    def _parse(self, raw: str, article_id: str) -> JudgeResult:
        raw = raw.strip()
        start, end = raw.find("{"), raw.rfind("}") + 1
        try:
            data = json.loads(raw[start:end])
            result = JudgeResult.model_validate(data)
            result.article_id = article_id
            return result
        except Exception:
            return JudgeResult(
                verdict="FAIL", confidence=0.0,
                critique="Judge returned unparseable output.",
                dimension_scores={"coverage": 0, "accuracy": 0,
                                  "structure": 0, "style": 0, "citations": 0},
                article_id=article_id,
            )
