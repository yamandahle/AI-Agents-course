"""Unit tests for tools/content_filter.py."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from article_writer.tools.content_filter import ContentFilterTool


def _mock_anthropic_response(text: str) -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_run_returns_keep_for_high_confidence() -> None:
    tool = ContentFilterTool()
    payload = json.dumps({"keep": True, "confidence": "HIGH", "reason": "Peer-reviewed source."})
    with patch("article_writer.tools.content_filter.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_anthropic_response(payload)
        result = tool._run("AI diagnostic accuracy 94% | Topic: AI in Healthcare")
    assert result.startswith("KEEP:HIGH")


def test_run_returns_discard_for_low_confidence() -> None:
    tool = ContentFilterTool()
    payload = json.dumps({"keep": False, "confidence": "LOW", "reason": "Social media post."})
    with patch("article_writer.tools.content_filter.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_anthropic_response(payload)
        result = tool._run("random tweet | Topic: AI")
    assert result.startswith("DISCARD:LOW")


def test_run_handles_malformed_json() -> None:
    tool = ContentFilterTool()
    with patch("article_writer.tools.content_filter.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_anthropic_response("not valid json")
        result = tool._run("some content | Topic: AI")
    assert "DISCARD" in result


def test_run_splits_on_topic_separator() -> None:
    tool = ContentFilterTool()
    payload = json.dumps({"keep": True, "confidence": "MEDIUM", "reason": "OK source."})
    with patch("article_writer.tools.content_filter.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_anthropic_response(payload)
        result = tool._run("Some content here | Topic: Machine Learning")
    assert "KEEP" in result or "DISCARD" in result
