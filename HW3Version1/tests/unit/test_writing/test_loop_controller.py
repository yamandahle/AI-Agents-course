"""Unit tests for writing/loop_controller.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from article_writer.writing.loop_controller import EvalOptimizerLoop


def _make_mock_score(weighted: float) -> MagicMock:
    score = MagicMock()
    score.weighted_score = weighted
    score.critique_points = ["Improve citation quality."]
    return score


def test_loop_runs_minimum_2_iterations(tmp_path: Path, sample_draft_tex: Path) -> None:
    loop = EvalOptimizerLoop(max_iterations=3, score_threshold=8.0)
    call_count = 0

    def mock_evaluate(draft_path: Path, iteration: int) -> MagicMock:
        nonlocal call_count
        call_count += 1
        return _make_mock_score(10.0)

    with patch("article_writer.writing.loop_controller.Evaluator") as MockEval, \
         patch("article_writer.writing.loop_controller.Optimizer") as MockOpt:
        MockEval.return_value.evaluate.side_effect = mock_evaluate
        MockOpt.return_value.optimize.return_value = sample_draft_tex
        loop.run(sample_draft_tex)

    assert call_count >= 2


def test_loop_stops_at_max_iterations(tmp_path: Path, sample_draft_tex: Path) -> None:
    loop = EvalOptimizerLoop(max_iterations=2, score_threshold=10.0)
    call_count = 0

    def mock_evaluate(draft_path: Path, iteration: int) -> MagicMock:
        nonlocal call_count
        call_count += 1
        return _make_mock_score(1.0)

    with patch("article_writer.writing.loop_controller.Evaluator") as MockEval, \
         patch("article_writer.writing.loop_controller.Optimizer") as MockOpt:
        MockEval.return_value.evaluate.side_effect = mock_evaluate
        MockOpt.return_value.optimize.return_value = sample_draft_tex
        loop.run(sample_draft_tex)

    assert call_count == 2


def test_loop_returns_path(tmp_path: Path, sample_draft_tex: Path) -> None:
    loop = EvalOptimizerLoop(max_iterations=2, score_threshold=0.0)
    with patch("article_writer.writing.loop_controller.Evaluator") as MockEval, \
         patch("article_writer.writing.loop_controller.Optimizer") as MockOpt:
        MockEval.return_value.evaluate.return_value = _make_mock_score(9.0)
        MockOpt.return_value.optimize.return_value = sample_draft_tex
        result = loop.run(sample_draft_tex)
    assert isinstance(result, Path)
