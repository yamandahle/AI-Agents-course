"""Editor — applies structured ReviewComment list to a draft with guideline-first priority."""
from __future__ import annotations

from pathlib import Path

from article_writer.shared.llm_client import LLMClient
from article_writer.writing.reviewer import ArticleReview
from article_writer.writing.few_shot_loader import FewShotLoader

_EDITOR_SYSTEM = """\
You are an expert academic article editor for MDPI journals.
You receive a LaTeX draft and a structured list of review comments.
Apply ALL corrections prioritised in this order:
  1. Guideline violations (Coverage, Accuracy, Citation)
  2. Research accuracy issues
  3. Writing profile violations (Structure, Terminology, Characters)

Rules:
- Return ONLY valid LaTeX source — no prose, no markdown outside LaTeX comments.
- Preserve all LaTeX preamble, \\begin{{document}}, \\maketitle, \\tableofcontents, \\end{{document}}.
- Each correction must be minimal — do not rewrite unrelated sections.
- If a comment says a citation is missing, add \\cite{{key}} inline; add the bib entry to the bibliography section.
"""


def _strip_code_fence(text: str) -> str:
    import re
    text = text.strip()
    m = re.search(r"```(?:latex|tex)?\s*([\s\S]+?)\s*```\s*$", text)
    return m.group(1).strip() if m else text


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


class Editor:
    """Applies a ReviewComment list to produce the next draft version."""

    def __init__(self, llm: LLMClient | None = None,
                 few_shot_dir: str | Path = "few_shot_examples") -> None:
        self._llm = llm or LLMClient()
        self._few_shot_dir = Path(few_shot_dir)

    def apply(
        self,
        draft_path: str | Path,
        review: ArticleReview,
        guideline_path: str | Path = "data/guideline.md",
        research_path: str | Path = "data/research.md",
        profiles_dir: str | Path = "profiles",
        version: int = 2,
    ) -> Path:
        draft = _load(Path(draft_path))
        guideline = _load(Path(guideline_path))
        research = _load(Path(research_path))
        profiles = self._load_profiles(Path(profiles_dir))
        few_shots = FewShotLoader(self._few_shot_dir).build_context_block()
        comments_text = self._format_comments(review)
        user_msg = (
            f"## GUIDELINE\n{guideline}\n\n"
            f"## RESEARCH\n{research}\n\n"
            f"## WRITING PROFILES\n{profiles}\n\n"
            f"{few_shots}\n\n"
            f"## REVIEW COMMENTS TO FIX\n{comments_text}\n\n"
            f"## CURRENT DRAFT\n{draft}\n\n"
            "Now output the corrected full LaTeX draft:"
        )
        resp = self._llm.complete(
            system=_EDITOR_SYSTEM,
            user=user_msg,
            step=f"edit:draft_v{version}",
            temperature=0.2,
            max_tokens=32768,
        )
        out_path = Path("results") / f"draft_v{version}.tex"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(_strip_code_fence(resp.text), encoding="utf-8")
        return out_path

    def _format_comments(self, review: ArticleReview) -> str:
        priority_order = ["Coverage", "Accuracy", "Citation", "Structure", "Terminology", "Characters"]
        sorted_comments = sorted(
            review.comments,
            key=lambda c: priority_order.index(c.profile)
            if c.profile in priority_order else 99,
        )
        lines = [f"Overall: {review.overall_score}/10 ({review.pass_fail})"]
        for i, c in enumerate(sorted_comments, 1):
            lines.append(f"{i}. [{c.profile}] {c.location} — {c.comment}")
        return "\n".join(lines)

    def _load_profiles(self, profiles_dir: Path) -> str:
        parts: list[str] = []
        for md in sorted(profiles_dir.glob("*.md")):
            parts.append(f"### {md.stem}\n{md.read_text(encoding='utf-8')}")
        return "\n\n".join(parts)
