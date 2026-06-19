from __future__ import annotations

import pytest

from hw4.shared.provider import load_provider


@pytest.mark.parametrize("provider,key_env,expected_model", [
    ("openai",    "OPENAI_API_KEY",    "gpt-4o-mini"),
    ("gemini",    "GEMINI_API_KEY",    "gemini/gemini-2.5-flash"),
    ("anthropic", "ANTHROPIC_API_KEY", "anthropic/claude-haiku-4-5-20251001"),
])
def test_load_provider_defaults(monkeypatch, provider, key_env, expected_model) -> None:
    monkeypatch.setenv("LLM_PROVIDER", provider)
    monkeypatch.setenv(key_env, "test-key-123")
    cfg = load_provider()
    assert cfg.name == provider
    assert cfg.model == expected_model
    assert cfg.api_key == "test-key-123"
    assert cfg.rate_limit_key == provider


def test_load_provider_custom_model(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini/gemini-1.5-pro")
    cfg = load_provider()
    assert cfg.model == "gemini/gemini-1.5-pro"


def test_load_provider_defaults_to_openai(monkeypatch) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    cfg = load_provider()
    assert cfg.name == "openai"


def test_load_provider_unknown_raises(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "cohere")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        load_provider()


def test_is_configured_true(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "real-key")
    assert load_provider().is_configured() is True


def test_is_configured_false_placeholder(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "your_key_here")
    assert load_provider().is_configured() is False


def test_is_configured_false_empty(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert load_provider().is_configured() is False
