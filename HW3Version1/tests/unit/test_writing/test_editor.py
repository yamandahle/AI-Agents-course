"""Tests for writing/editor.py — applies ReviewComment list to produce next draft."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from article_writer.writing.reviewer import ArticleReview, ReviewComment


def _make_review(profile: str = "Coverage") -> ArticleReview:
    return ArticleReview(
        comments=[ReviewComment(profile=profile, location="Section 1", comment="Needs more detail")],
        overall_score=6.0,
        pass_fail="FAIL",
    )


def test_format_comments_puts_coverage_first() -> None:
    from article_writer.writing.editor import Editor
    mock_llm = MagicMock()
    ed = Editor(llm=mock_llm)
    review = ArticleReview(
        comments=[
            ReviewComment(profile="Structure", location="s1", comment="bad structure"),
            ReviewComment(profile="Coverage", location="s2", comment="missing coverage"),
        ],
        overall_score=5.0,
        pass_fail="FAIL",
    )
    result = ed._format_comments(review)
    assert result.index("Coverage") < result.index("Structure")


def test_format_comments_puts_accuracy_before_terminology() -> None:
    from article_writer.writing.editor import Editor
    ed = Editor(llm=MagicMock())
    review = ArticleReview(
        comments=[
            ReviewComment(profile="Terminology", location="s1", comment="wrong term"),
            ReviewComment(profile="Accuracy", location="s2", comment="wrong fact"),
        ],
        overall_score=5.0,
        pass_fail="FAIL",
    )
    result = ed._format_comments(review)
    assert result.index("Accuracy") < result.index("Terminology")


def test_apply_saves_to_correct_path(tmp_path: Path, monkeypatch) -> None:
    from article_writer.writing.editor import Editor
    monkeypatch.chdir(tmp_path)
    (tmp_path / "results").mkdir()
    draft_file = tmp_path / "draft.tex"
    draft_file.write_text(r"\begin{document}\end{document}", encoding="utf-8")

    mock_resp = MagicMock()
    mock_resp.text = r"\begin{document}corrected\end{document}"
    mock_llm = MagicMock()
    mock_llm.complete.return_value = mock_resp

    review = _make_review()
    ed = Editor(llm=mock_llm)
    result = ed.apply(draft_file, review, version=3)
    assert result.name == "draft_v3.tex"
    assert result.exists()


def test_apply_prompt_includes_few_shots(tmp_path: Path, monkeypatch) -> None:
    from article_writer.writing.editor import Editor
    monkeypatch.chdir(tmp_path)
    (tmp_path / "results").mkdir()
    (tmp_path / "few_shot_examples").mkdir()
    (tmp_path / "few_shot_examples" / "example.md").write_text("# Example\nContent", encoding="utf-8")
    draft_file = tmp_path / "draft.tex"
    draft_file.write_text(r"\begin{document}\end{document}", encoding="utf-8")

    mock_resp = MagicMock()
    mock_resp.text = r"\begin{document}\end{document}"
    mock_llm = MagicMock()
    mock_llm.complete.return_value = mock_resp

    review = _make_review()
    ed = Editor(llm=mock_llm, few_shot_dir=tmp_path / "few_shot_examples")
    ed.apply(draft_file, review, version=2)

    call_kwargs = mock_llm.complete.call_args
    user_msg = call_kwargs[1]["user"] if call_kwargs[1] else call_kwargs[0][1]
    assert "FEW-SHOT" in user_msg or "Example" in user_msg
