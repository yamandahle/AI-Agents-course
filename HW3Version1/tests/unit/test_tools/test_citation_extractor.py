"""Tests for tools/citation_extractor.py — formats citations from URLs or text."""
from __future__ import annotations

import json
from unittest.mock import patch

from article_writer.tools.citation_extractor import CitationExtractorTool


def _tool() -> CitationExtractorTool:
    return CitationExtractorTool()


def _mock_api_response(data: dict):
    from article_writer.shared.llm_client import LLMResponse
    return LLMResponse(text=json.dumps(data), input_tokens=10, output_tokens=20, model="mock", cost_usd=0.0)


def test_run_detects_url_input() -> None:
    tool = _tool()
    data = {"title": "Study", "author": "Smith", "date": "2024-01-01", "url": "https://example.com"}
    with patch("article_writer.tools.citation_extractor.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_api_response(data)
        result = tool._run("https://example.com/paper")
    assert "[Study]" in result
    assert "Smith" in result


def test_run_detects_plain_text_input() -> None:
    tool = _tool()
    data = {"title": "My Paper", "author": "Jones", "date": "2023-05-10", "publication": "Nature"}
    with patch("article_writer.tools.citation_extractor.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_api_response(data)
        result = tool._run("A paper by Jones about things")
    assert "My Paper" in result
    assert "Jones" in result


def test_run_returns_fallback_on_api_error() -> None:
    tool = _tool()
    with patch("article_writer.tools.citation_extractor.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.side_effect = RuntimeError("API down")
        result = tool._run("some text passage")
    assert "source unverified" in result


def test_run_formats_markdown_citation() -> None:
    tool = _tool()
    data = {"title": "AI Study", "author": "Lee", "date": "2024-03-15", "url": "http://ai.com"}
    with patch("article_writer.tools.citation_extractor.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_api_response(data)
        result = tool._run("http://ai.com")
    assert "[AI Study](http://ai.com)" in result
