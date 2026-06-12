"""Tests for writing/evaluator.py — draft scoring and critique writing."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch


def _mock_response(data: dict) -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=json.dumps(data))]
    return msg


def _good_scores() -> dict:
    return {
        "coverage": 8, "accuracy": 7, "style": 9,
        "structure": 8, "citation_quality": 7,
        "critique_points": ["Improve citations.", "Add more examples."],
    }


def test_evaluate_returns_evaluation_score(tmp_path: Path) -> None:
    draft = tmp_path / "draft_v1.tex"
    draft.write_text(r"\begin{document}Hello\end{document}", encoding="utf-8")
    mock_msg = _mock_response(_good_scores())
    with patch("anthropic.Anthropic") as MockAnthro, \
         patch("article_writer.writing.evaluator.RESULTS_DIR", str(tmp_path)):
        MockAnthro.return_value.messages.create.return_value = mock_msg
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.evaluator.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.evaluator import Evaluator
            ev = Evaluator()
            score = ev.evaluate(draft, iteration=1)
    assert score.coverage == 8.0
    assert score.accuracy == 7.0
    assert score.weighted_score > 0
    assert len(score.critique_points) == 2


def test_evaluate_writes_critique_file(tmp_path: Path) -> None:
    draft = tmp_path / "draft_v1.tex"
    draft.write_text(r"\begin{document}Content\end{document}", encoding="utf-8")
    mock_msg = _mock_response(_good_scores())
    with patch("anthropic.Anthropic") as MockAnthro, \
         patch("article_writer.writing.evaluator.RESULTS_DIR", str(tmp_path)):
        MockAnthro.return_value.messages.create.return_value = mock_msg
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.evaluator.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.evaluator import Evaluator
            ev = Evaluator()
            ev.evaluate(draft, iteration=2)
    critique_file = tmp_path / "critique_v2.md"
    assert critique_file.exists()
    content = critique_file.read_text(encoding="utf-8")
    assert "Iteration 2" in content
    assert "Improve citations" in content


def test_evaluate_clamps_scores_to_1_to_10(tmp_path: Path) -> None:
    draft = tmp_path / "draft.tex"
    draft.write_text(r"\begin{document}x\end{document}", encoding="utf-8")
    bad_data = {
        "coverage": 15, "accuracy": -3, "style": 5,
        "structure": 0, "citation_quality": 11,
        "critique_points": [],
    }
    mock_msg = _mock_response(bad_data)
    with patch("anthropic.Anthropic"), \
         patch("article_writer.writing.evaluator.RESULTS_DIR", str(tmp_path)):
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.evaluator.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.evaluator import Evaluator
            ev = Evaluator()
            score = ev.evaluate(draft, iteration=1)
    assert score.coverage == 10.0
    assert score.accuracy == 1.0
    assert score.citation_quality == 10.0


def test_evaluate_missing_keys_default_to_5(tmp_path: Path) -> None:
    draft = tmp_path / "draft.tex"
    draft.write_text(r"\begin{document}x\end{document}", encoding="utf-8")
    mock_msg = _mock_response({"critique_points": []})
    with patch("anthropic.Anthropic"), \
         patch("article_writer.writing.evaluator.RESULTS_DIR", str(tmp_path)):
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.evaluator.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.evaluator import Evaluator
            ev = Evaluator()
            score = ev.evaluate(draft, iteration=1)
    assert score.coverage == 5.0
    assert score.accuracy == 5.0
