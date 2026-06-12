"""Unit tests for Reviewer and ArticleReview (writing/reviewer.py)."""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from article_writer.writing.reviewer import Reviewer, ArticleReview, ReviewComment


def _make_mock_llm(text: str):
    mock = MagicMock()
    response = MagicMock()
    response.text = text
    mock.complete.return_value = response
    return mock


_VALID_REVIEW_JSON = json.dumps({
    "comments": [
        {"profile": "Coverage", "location": "Section 1", "comment": "Missing key point."},
        {"profile": "Accuracy", "location": "Abstract, line 3", "comment": "Unsupported claim."},
    ],
    "overall_score": 6.5,
    "pass_fail": "FAIL",
})

_PASS_REVIEW_JSON = json.dumps({
    "comments": [],
    "overall_score": 9.0,
    "pass_fail": "PASS",
})


def test_parse_valid_json_returns_article_review():
    reviewer = Reviewer(llm=_make_mock_llm(_VALID_REVIEW_JSON))
    result = reviewer._parse(_VALID_REVIEW_JSON)
    assert isinstance(result, ArticleReview)
    assert len(result.comments) == 2
    assert result.overall_score == 6.5
    assert result.pass_fail == "FAIL"


def test_parse_invalid_json_returns_fallback():
    reviewer = Reviewer(llm=_make_mock_llm("not json at all"))
    result = reviewer._parse("not json at all")
    assert result.pass_fail == "FAIL"
    assert result.overall_score == 0.0


def test_parse_pass_review():
    reviewer = Reviewer(llm=_make_mock_llm(_PASS_REVIEW_JSON))
    result = reviewer._parse(_PASS_REVIEW_JSON)
    assert result.pass_fail == "PASS"
    assert result.comments == []


def test_review_comment_fields():
    c = ReviewComment(profile="Structure", location="Section 2", comment="Missing subsection.")
    assert c.profile == "Structure"
    assert c.location == "Section 2"
    assert c.comment == "Missing subsection."


def test_review_does_not_include_few_shots(tmp_path):
    (tmp_path / "guideline.md").write_text("## Guideline", encoding="utf-8")
    (tmp_path / "research.md").write_text("## Research", encoding="utf-8")
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "Structure.md").write_text("Structure rules", encoding="utf-8")
    draft = tmp_path / "draft_v1.tex"
    draft.write_text(r"\begin{document}\end{document}", encoding="utf-8")
    mock_llm = _make_mock_llm(_VALID_REVIEW_JSON)
    reviewer = Reviewer(llm=mock_llm)
    reviewer.review(draft, tmp_path / "guideline.md",
                    tmp_path / "research.md", profiles)
    call_args = mock_llm.complete.call_args
    user_msg = call_args[1].get("user", "") or call_args[0][1]
    assert "FEW-SHOT" not in user_msg.upper()
    assert "few_shot" not in user_msg.lower()


def test_reviewer_pydantic_model_validate():
    data = {
        "comments": [{"profile": "Citation", "location": "Ref 3", "comment": "Dead link."}],
        "overall_score": 7.5,
        "pass_fail": "FAIL",
    }
    review = ArticleReview.model_validate(data)
    assert review.comments[0].profile == "Citation"
