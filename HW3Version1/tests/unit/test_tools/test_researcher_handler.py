"""Tests for tools/researcher_handler.py — session-aware research query manager."""
from __future__ import annotations

import json
from unittest.mock import patch

from article_writer.tools.researcher_handler import ResearcherHandlerTool


def _make_mock_response(text: str):
    from article_writer.shared.llm_client import LLMResponse
    return LLMResponse(text=text, input_tokens=10, output_tokens=20, model="mock", cost_usd=0.0)


def test_run_increments_batch_count() -> None:
    tool = ResearcherHandlerTool()
    llm_json = json.dumps({"new_queries": ["q1", "q2", "q3"], "summary_so_far": "done"})
    with patch("article_writer.tools.researcher_handler.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _make_mock_response(llm_json)
        tool._run("AI research")
        tool._run("ML research")
    assert tool._session.batch_count == 2


def test_reset_session_clears_state() -> None:
    tool = ResearcherHandlerTool()
    tool._session.batch_count = 5
    tool._session.previous_queries = ["q1", "q2"]
    tool.reset_session()
    assert tool._session.batch_count == 0
    assert tool._session.previous_queries == []


def test_run_output_is_valid_json() -> None:
    tool = ResearcherHandlerTool()
    llm_json = json.dumps({"new_queries": ["a", "b", "c"], "summary_so_far": "ok"})
    with patch("article_writer.tools.researcher_handler.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _make_mock_response(llm_json)
        result = tool._run("topic")
    parsed = json.loads(result)
    assert "new_queries" in parsed
    assert "batch" in parsed


def test_run_uses_fallback_on_json_error() -> None:
    tool = ResearcherHandlerTool()
    with patch("article_writer.tools.researcher_handler.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.side_effect = RuntimeError("API down")
        result = tool._run("topic")
    parsed = json.loads(result)
    assert len(parsed["new_queries"]) == 3
