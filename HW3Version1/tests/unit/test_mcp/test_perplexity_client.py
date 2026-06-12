"""Tests for mcp/perplexity_client.py — Perplexity API fallback search client."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _make_perplexity_response(content: str = "perplexity answer") -> MagicMock:
    resp = MagicMock()
    resp.choices = [MagicMock(message=MagicMock(content=content))]
    resp.usage = MagicMock(prompt_tokens=40, completion_tokens=20)
    resp.citations = []
    return resp


def test_perplexity_client_raises_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    with patch("openai.OpenAI"):
        from importlib import reload
        import article_writer.mcp.perplexity_client as pc
        reload(pc)
        with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
            pc.PerplexityClient(gatekeeper=MagicMock())


def test_perplexity_client_search_returns_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")
    resp = _make_perplexity_response("ML is cool")
    mock_gate = MagicMock()
    mock_gate.execute.return_value = resp
    with patch("openai.OpenAI"):
        from importlib import reload
        import article_writer.mcp.perplexity_client as pc
        reload(pc)
        client = pc.PerplexityClient(gatekeeper=mock_gate)
        result = client.search("What is ML?")
    assert result["answer"] == "ML is cool"
    assert result["confidence"] == "MEDIUM"
    assert result["citations"] == []


def test_perplexity_client_extract_citations_from_string_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")
    resp = _make_perplexity_response()
    resp.citations = ["https://example.com", "https://other.com"]
    mock_gate = MagicMock()
    mock_gate.execute.return_value = resp
    with patch("openai.OpenAI"):
        from importlib import reload
        import article_writer.mcp.perplexity_client as pc
        reload(pc)
        client = pc.PerplexityClient(gatekeeper=mock_gate)
        result = client.search("query")
    assert len(result["citations"]) == 2
    assert result["citations"][0]["url"] == "https://example.com"


def test_perplexity_client_extract_citations_from_dict_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")
    resp = _make_perplexity_response()
    resp.citations = [{"title": "Paper", "url": "https://paper.com"}]
    mock_gate = MagicMock()
    mock_gate.execute.return_value = resp
    with patch("openai.OpenAI"):
        from importlib import reload
        import article_writer.mcp.perplexity_client as pc
        reload(pc)
        client = pc.PerplexityClient(gatekeeper=mock_gate)
        result = client.search("query")
    assert result["citations"][0]["title"] == "Paper"
