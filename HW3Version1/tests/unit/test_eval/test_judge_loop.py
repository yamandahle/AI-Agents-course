"""Tests for eval/judge_loop.py — F1-guided iterative judge prompt refinement."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from article_writer.eval.judge_loop import JudgeLoop
from article_writer.eval.f1_metrics import F1Result


def _make_samples(labels: list[str]) -> list[dict]:
    return [
        {"article_id": f"art_{i}", "full_text": "text " * 100, "abstract": "abstract", "label": lbl}
        for i, lbl in enumerate(labels)
    ]


def _mock_llm(verdict: str = "PASS", refine_text: str = "refined prompt") -> MagicMock:
    judge_resp = MagicMock()
    judge_resp.text = json.dumps({
        "verdict": verdict, "confidence": 0.9, "critique": "A. B. C.",
        "dimension_scores": {"coverage": 8, "accuracy": 8, "structure": 8, "style": 8, "citations": 8},
    })
    refine_resp = MagicMock()
    refine_resp.text = refine_text
    llm = MagicMock()
    llm.complete.side_effect = [judge_resp, judge_resp, refine_resp] * 20
    return llm


def test_run_result_has_required_keys() -> None:
    dev = _make_samples(["PASS", "PASS"])
    test = _make_samples(["PASS"])
    loop = JudgeLoop(llm=_mock_llm("PASS"), f1_target=0.80, max_iterations=2)
    result = loop.run(dev, test)
    assert "test_f1" in result
    assert "dev_f1_history" in result
    assert "final_prompt" in result
    assert "iterations" in result


def test_run_early_stop_when_f1_target_met() -> None:
    dev = _make_samples(["PASS", "PASS"])
    test = _make_samples(["PASS"])
    loop = JudgeLoop(llm=_mock_llm("PASS"), f1_target=0.0, max_iterations=5)
    result = loop.run(dev, test)
    assert result["iterations"] == 1


def test_run_respects_max_iterations() -> None:
    dev = _make_samples(["PASS", "FAIL"])
    test = _make_samples(["PASS"])
    llm = _mock_llm("PASS")
    loop = JudgeLoop(llm=llm, f1_target=1.0, max_iterations=2)
    result = loop.run(dev, test)
    assert result["iterations"] <= 2


def test_describe_errors_labels_fp_and_fn() -> None:
    loop = JudgeLoop(llm=MagicMock(), f1_target=0.8, max_iterations=1)
    samples = _make_samples(["PASS", "FAIL"])
    preds = ["FAIL", "PASS"]
    labels = ["PASS", "FAIL"]
    desc = loop._describe_errors(samples, preds, labels)
    assert "FN" in desc
    assert "FP" in desc


def test_evaluate_split_returns_equal_length_lists() -> None:
    loop = JudgeLoop(llm=_mock_llm("PASS"), f1_target=0.8, max_iterations=1)
    samples = _make_samples(["PASS", "FAIL", "PASS"])
    from article_writer.eval.judge import ArticleJudge
    judge = ArticleJudge(llm=loop._llm)
    preds, labels = loop._evaluate_split(judge, samples)
    assert len(preds) == len(labels) == 3
