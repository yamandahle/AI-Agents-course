from __future__ import annotations

from unittest.mock import MagicMock

from hw4.shared.llm_client import LlmClient


def test_llm_client_not_configured_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LlmClient(MagicMock())
    assert client.is_configured() is False
    assert client.complete("sys", "user") == ""
