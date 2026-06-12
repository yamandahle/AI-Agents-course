"""Tests for tools/deep_research_tool.py — Gemini/Perplexity web research tool."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from article_writer.tools.deep_research_tool import DeepResearchTool


def _tool() -> DeepResearchTool:
    return DeepResearchTool()


def test_run_returns_markdown_with_answer_and_citations() -> None:
    tool = _tool()
    gemini_result = {
        "answer": "AI is transforming healthcare.",
        "citations": [{"title": "Study", "url": "http://example.com"}],
        "confidence": "HIGH",
    }
    with patch.object(tool, "_try_gemini", return_value=gemini_result):
        result = tool._run("AI in healthcare")
    assert "## Answer" in result
    assert "## Citations" in result
    assert "HIGH" in result


def test_run_falls_back_to_perplexity_when_gemini_fails() -> None:
    tool = _tool()
    perplexity_result = {
        "answer": "Fallback answer.",
        "citations": [],
        "confidence": "MEDIUM",
    }
    with patch.object(tool, "_try_gemini", return_value=None), \
         patch.object(tool, "_try_perplexity", return_value=perplexity_result):
        result = tool._run("some query")
    assert "Fallback answer" in result


def test_run_returns_empty_string_on_low_confidence() -> None:
    tool = _tool()
    low_result = {"answer": "Junk", "citations": [], "confidence": "LOW"}
    with patch.object(tool, "_try_gemini", return_value=low_result):
        result = tool._run("bad query")
    assert result == ""


def test_run_returns_empty_string_when_both_fail() -> None:
    tool = _tool()
    with patch.object(tool, "_try_gemini", return_value=None), \
         patch.object(tool, "_try_perplexity", return_value=None):
        result = tool._run("unreachable query")
    assert result == ""


def test_format_result_no_citations_shows_placeholder() -> None:
    tool = _tool()
    result = tool._format_result({"answer": "answer", "citations": [], "confidence": "HIGH"})
    assert "(no citations returned)" in result
