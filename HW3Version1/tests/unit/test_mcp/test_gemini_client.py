"""Tests for mcp/gemini_client.py — Gemini API search client."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _make_gemini_response(text: str = "answer", has_citations: bool = True) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    resp.usage_metadata = MagicMock(prompt_token_count=50, candidates_token_count=30)
    if has_citations:
        chunk = MagicMock()
        chunk.web.title = "Paper Title"
        chunk.web.uri = "https://example.com"
        resp.candidates = [MagicMock(grounding_metadata=MagicMock(grounding_chunks=[chunk]))]
    else:
        resp.candidates = [MagicMock(grounding_metadata=MagicMock(grounding_chunks=[]))]
    return resp


def test_gemini_client_raises_without_api_key() -> None:
    mock_genai = MagicMock()
    with patch.dict("sys.modules", {"google.generativeai": mock_genai}), \
         patch("article_writer.mcp.gemini_client.os.environ.get", return_value=None):
        import article_writer.mcp.gemini_client as gm
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            gm.GeminiClient(gatekeeper=MagicMock())


def test_gemini_client_search_returns_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    resp = _make_gemini_response("AI is great")
    mock_gate = MagicMock()
    mock_gate.execute.return_value = resp
    with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
        from importlib import reload
        import article_writer.mcp.gemini_client as gm
        reload(gm)
        client = gm.GeminiClient(gatekeeper=mock_gate)
        result = client.search("What is AI?")
    assert result["answer"] == "AI is great"
    assert result["confidence"] == "HIGH"
    assert len(result["citations"]) == 1
    assert result["citations"][0]["title"] == "Paper Title"


def test_gemini_client_search_medium_confidence_no_citations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_genai = MagicMock()
    mock_genai.GenerativeModel.return_value = MagicMock()
    resp = _make_gemini_response("answer", has_citations=False)
    mock_gate = MagicMock()
    mock_gate.execute.return_value = resp
    with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
        from importlib import reload
        import article_writer.mcp.gemini_client as gm
        reload(gm)
        client = gm.GeminiClient(gatekeeper=mock_gate)
        result = client.search("query")
    assert result["confidence"] == "MEDIUM"
    assert result["citations"] == []


def test_gemini_client_extract_citations_handles_attribute_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_genai = MagicMock()
    mock_genai.GenerativeModel.return_value = MagicMock()
    resp = MagicMock()
    resp.text = "answer"
    resp.usage_metadata = None
    resp.candidates = MagicMock(side_effect=AttributeError)
    mock_gate = MagicMock()
    mock_gate.execute.return_value = resp
    with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
        from importlib import reload
        import article_writer.mcp.gemini_client as gm
        reload(gm)
        client = gm.GeminiClient(gatekeeper=mock_gate)
        citations = client._extract_citations(resp)
    assert citations == []
