from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hw4.shared.llm_client import LlmClient


def _make_client(monkeypatch, provider: str, key: str, model: str | None = None) -> LlmClient:
    monkeypatch.setenv("LLM_PROVIDER", provider)
    key_env = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}[provider]
    monkeypatch.setenv(key_env, key)
    if model:
        model_env = {"openai": "OPENAI_MODEL", "gemini": "GEMINI_MODEL", "anthropic": "ANTHROPIC_MODEL"}[provider]
        monkeypatch.setenv(model_env, model)
    return LlmClient(MagicMock())


@pytest.mark.parametrize("provider", ["openai", "gemini", "anthropic"])
def test_not_configured_without_key(monkeypatch, provider: str) -> None:
    monkeypatch.setenv("LLM_PROVIDER", provider)
    key_env = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}[provider]
    monkeypatch.delenv(key_env, raising=False)
    client = LlmClient(MagicMock())
    assert client.is_configured() is False
    assert client.complete("sys", "user") == ""


@pytest.mark.parametrize("provider", ["openai", "gemini", "anthropic"])
def test_not_configured_with_placeholder(monkeypatch, provider: str) -> None:
    client = _make_client(monkeypatch, provider, "your_key_here")
    assert client.is_configured() is False


@pytest.mark.parametrize("provider,expected_model", [
    ("openai", "gpt-4o-mini"),
    ("gemini", "gemini/gemini-2.5-flash"),
    ("anthropic", "anthropic/claude-haiku-4-5-20251001"),
])
def test_default_model_per_provider(monkeypatch, provider: str, expected_model: str) -> None:
    client = _make_client(monkeypatch, provider, "real-key-abc")
    assert client._provider.model == expected_model


def test_complete_calls_litellm(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "real-key-abc")
    gatekeeper = MagicMock()
    gatekeeper.execute.side_effect = lambda fn, *a, **kw: fn(*a, **kw)
    client = LlmClient(gatekeeper)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "hello"
    with patch("hw4.shared.llm_client.litellm.completion", return_value=mock_response) as mock_llm:
        result = client.complete("system prompt", "user prompt")
    assert result == "hello"
    mock_llm.assert_called_once()
    call_kwargs = mock_llm.call_args.kwargs
    assert call_kwargs["model"] == "gemini/gemini-2.5-flash"
    assert call_kwargs["api_key"] == "real-key-abc"
