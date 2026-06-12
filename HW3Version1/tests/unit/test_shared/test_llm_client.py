"""Tests for shared/llm_client.py — unified Anthropic/Google LLM abstraction."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _mock_anthropic_client() -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text="response text")]
    msg.usage.input_tokens = 100
    msg.usage.output_tokens = 50
    client = MagicMock()
    client.messages.create.return_value = msg
    return client


def _mock_google_model() -> MagicMock:
    resp = MagicMock()
    resp.text = "google response"
    meta = MagicMock()
    meta.prompt_token_count = 80
    meta.candidates_token_count = 40
    resp.usage_metadata = meta
    model = MagicMock()
    model.generate_content.return_value = resp
    return model


def test_anthropic_provider_init(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("anthropic.Anthropic", return_value=_mock_anthropic_client()):
        from article_writer.shared.llm_client import LLMClient
        client = LLMClient(provider="anthropic")
    assert client.provider == "anthropic"
    assert client.model == "claude-sonnet-4-6"


def test_unknown_provider_raises() -> None:
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        from article_writer.shared.llm_client import LLMClient
        LLMClient(provider="invalid-provider")


def test_complete_returns_llm_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = _mock_anthropic_client()
    with patch("anthropic.Anthropic", return_value=mock_client):
        from article_writer.shared.llm_client import LLMClient
        client = LLMClient(provider="anthropic")
        resp = client.complete(system="be helpful", user="hello")
    assert resp.text == "response text"
    assert resp.input_tokens == 100
    assert resp.output_tokens == 50
    assert resp.model == "claude-sonnet-4-6"
    assert resp.cost_usd >= 0.0


def test_estimate_cost_known_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("anthropic.Anthropic", return_value=_mock_anthropic_client()):
        from article_writer.shared.llm_client import LLMClient, _InternalResult
        client = LLMClient(provider="anthropic")
        result = _InternalResult(text="x", input_tokens=1000, output_tokens=1000)
        cost = client._estimate_cost(result)
    assert cost == pytest.approx(0.003 + 0.015, rel=1e-3)


def test_estimate_cost_unknown_model_uses_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("anthropic.Anthropic", return_value=_mock_anthropic_client()):
        from article_writer.shared.llm_client import LLMClient, _InternalResult
        client = LLMClient(provider="anthropic")
        client.model = "unknown-model-xyz"
        result = _InternalResult(text="x", input_tokens=1000, output_tokens=1000)
        cost = client._estimate_cost(result)
    assert cost == pytest.approx(0.001 + 0.004, rel=1e-3)


def test_google_provider_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_model = _mock_google_model()
    mock_genai = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_genai.GenerationConfig.return_value = MagicMock()
    with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
        from importlib import reload
        import article_writer.shared.llm_client as llm_module
        reload(llm_module)
        client = llm_module.LLMClient(provider="google", model="gemini-2.0-flash")
        resp = client.complete(system="be helpful", user="hello")
    assert resp.text == "google response"
    assert resp.input_tokens == 80
    assert resp.output_tokens == 40
