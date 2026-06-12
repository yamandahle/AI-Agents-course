"""Integration tests for ReviewLoop (writing/review_loop.py)."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from article_writer.writing.reviewer import ArticleReview, ReviewComment
from article_writer.writing.review_loop import ReviewLoop


def _make_review(pass_fail: str = "FAIL", score: float = 5.0) -> str:
    return json.dumps({
        "comments": [{"profile": "Coverage", "location": "Section 1", "comment": "Issue."}],
        "overall_score": score,
        "pass_fail": pass_fail,
    })


def _make_mock_llm(review_text: str, edit_text: str = r"\begin{document}\end{document}"):
    mock = MagicMock()
    call_count = [0]

    def side_effect(*args, **kwargs):
        call_count[0] += 1
        resp = MagicMock()
        step = kwargs.get("step", "")
        resp.text = review_text if step.startswith("review") else edit_text
        return resp

    mock.complete.side_effect = side_effect
    return mock


@pytest.fixture
def setup_dirs(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "guideline.md").write_text("## Guideline", encoding="utf-8")
    (tmp_path / "data" / "research.md").write_text("## Research", encoding="utf-8")
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "Structure.md").write_text("Structure rules", encoding="utf-8")
    few_shots = tmp_path / "few_shot_examples"
    few_shots.mkdir()
    results = tmp_path / "results"
    results.mkdir()
    draft = results / "draft_v1.tex"
    draft.write_text(r"\begin{document}Initial draft\end{document}", encoding="utf-8")
    return tmp_path


def test_minimum_two_iterations(setup_dirs):
    tmp = setup_dirs
    mock_llm = _make_mock_llm(_make_review("PASS", 9.0))

    with (patch("article_writer.writing.reviewer.LLMClient", return_value=mock_llm),
          patch("article_writer.writing.editor.LLMClient", return_value=mock_llm)):
        loop = ReviewLoop(
            iterations=3,
            guideline_path=tmp / "data/guideline.md",
            research_path=tmp / "data/research.md",
            profiles_dir=tmp / "profiles",
            few_shot_dir=tmp / "few_shot_examples",
            results_dir=tmp / "results",
            llm=mock_llm,
        )
        final = loop.run(tmp / "results/draft_v1.tex")

    assert final.exists()
    assert final.name == "draft_final.tex"
    review_v1 = tmp / "results" / "review_v1.json"
    assert review_v1.exists()
    data = json.loads(review_v1.read_text())
    assert "pass_fail" in data


def test_draft_final_always_created(setup_dirs):
    tmp = setup_dirs
    mock_llm = _make_mock_llm(_make_review("FAIL", 3.0))

    with (patch("article_writer.writing.reviewer.LLMClient", return_value=mock_llm),
          patch("article_writer.writing.editor.LLMClient", return_value=mock_llm)):
        loop = ReviewLoop(
            iterations=2,
            guideline_path=tmp / "data/guideline.md",
            research_path=tmp / "data/research.md",
            profiles_dir=tmp / "profiles",
            few_shot_dir=tmp / "few_shot_examples",
            results_dir=tmp / "results",
            llm=mock_llm,
        )
        final = loop.run(tmp / "results/draft_v1.tex")

    assert (tmp / "results" / "draft_final.tex").exists()


def test_iterations_clamped_between_2_and_4(setup_dirs):
    tmp = setup_dirs
    mock_llm = _make_mock_llm(_make_review("FAIL"))
    loop = ReviewLoop(iterations=10, results_dir=tmp / "results", llm=mock_llm)
    assert loop.iterations == 4


def test_iterations_minimum_is_2(setup_dirs):
    tmp = setup_dirs
    mock_llm = _make_mock_llm(_make_review("FAIL"))
    loop = ReviewLoop(iterations=1, results_dir=tmp / "results", llm=mock_llm)
    assert loop.iterations == 2
