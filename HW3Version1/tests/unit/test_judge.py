"""Unit tests for ArticleJudge (eval/judge.py)."""
import json
from unittest.mock import MagicMock

import pytest

from article_writer.eval.judge import ArticleJudge, JudgeResult


def _make_mock_llm(text: str):
    mock = MagicMock()
    resp = MagicMock()
    resp.text = text
    mock.complete.return_value = resp
    return mock


_VALID_JUDGE_JSON = json.dumps({
    "verdict": "PASS",
    "confidence": 0.85,
    "critique": "Well structured. Citations are adequate. Discussion is thorough.",
    "dimension_scores": {
        "coverage": 8, "accuracy": 9, "structure": 8, "style": 7, "citations": 9
    }
})

_FAIL_JUDGE_JSON = json.dumps({
    "verdict": "FAIL",
    "confidence": 0.9,
    "critique": "Missing results section. Claims lack citations. Structure is incomplete.",
    "dimension_scores": {
        "coverage": 4, "accuracy": 3, "structure": 2, "style": 6, "citations": 2
    }
})


def test_parse_valid_json_pass():
    judge = ArticleJudge(llm=_make_mock_llm(_VALID_JUDGE_JSON))
    result = judge._parse(_VALID_JUDGE_JSON, "art_001")
    assert result.verdict == "PASS"
    assert result.confidence == 0.85
    assert result.article_id == "art_001"
    assert len(result.dimension_scores) == 5


def test_parse_invalid_json_fallback():
    judge = ArticleJudge(llm=_make_mock_llm("garbage"))
    result = judge._parse("garbage", "art_002")
    assert result.verdict == "FAIL"
    assert result.confidence == 0.0
    assert "unparseable" in result.critique


def test_judge_result_dimension_scores_all_present():
    result = JudgeResult.model_validate(json.loads(_VALID_JUDGE_JSON))
    expected_keys = {"coverage", "accuracy", "structure", "style", "citations"}
    assert expected_keys <= set(result.dimension_scores.keys())


def test_judge_calls_llm_complete():
    mock_llm = _make_mock_llm(_VALID_JUDGE_JSON)
    judge = ArticleJudge(llm=mock_llm)
    judge.judge("article text", "guideline", "research", "art_001")
    mock_llm.complete.assert_called_once()


def test_judge_passes_article_to_prompt():
    mock_llm = _make_mock_llm(_VALID_JUDGE_JSON)
    judge = ArticleJudge(llm=mock_llm)
    judge.judge("UNIQUE_ARTICLE_CONTENT", "guideline", "research", "art_001")
    call_args = mock_llm.complete.call_args
    user_msg = call_args[1].get("user", "") or call_args[0][1]
    assert "UNIQUE_ARTICLE_CONTENT" in user_msg


def test_judge_fail_verdict():
    judge = ArticleJudge(llm=_make_mock_llm(_FAIL_JUDGE_JSON))
    result = judge.judge("text", "guideline", "research")
    assert result.verdict == "FAIL"


def test_judge_uses_custom_prompt():
    custom_prompt = "CUSTOM JUDGE PROMPT"
    mock_llm = _make_mock_llm(_VALID_JUDGE_JSON)
    judge = ArticleJudge(llm=mock_llm, prompt=custom_prompt)
    assert judge.prompt == custom_prompt
    judge.judge("text", "g", "r")
    call_args = mock_llm.complete.call_args
    system_msg = call_args[1].get("system", "") or call_args[0][0]
    assert "CUSTOM JUDGE PROMPT" in system_msg
