"""Tests for BaseAgent initialization, send_message, and receive_message."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from base_agent_test_helpers import make_agent, make_mock_response

from debate.agents.base_agent import DebateMessage


class TestInitialization:
    def test_initializes_with_correct_config(self) -> None:
        agent = make_agent(role="pro")
        assert agent._role == "pro"  # noqa: SLF001
        assert agent._model == "claude-haiku-4-5"  # noqa: SLF001
        assert agent._timeout == 5.0  # noqa: SLF001
        assert agent._word_limit == 150  # noqa: SLF001
        assert agent._max_tokens == 500  # noqa: SLF001

    def test_gatekeeper_stored_on_agent(self) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        agent = make_agent(gatekeeper=gk)
        assert agent._gatekeeper is gk  # noqa: SLF001


class TestSendMessage:
    def test_send_message_returns_debate_message(self) -> None:
        agent = make_agent()
        msg = agent.send_message("Remote work improves productivity", ping_num=2)
        assert isinstance(msg, DebateMessage)
        assert msg.sender == "pro"
        assert msg.type == "argument"
        assert msg.round == 2
        assert msg.content == "Remote work improves productivity"

    def test_send_message_produces_valid_json(self) -> None:
        agent = make_agent()
        msg = agent.send_message("hello world test", ping_num=3)
        parsed = json.loads(msg.to_json())
        assert parsed["type"] == "argument"
        assert parsed["sender"] == "pro"
        assert parsed["content"] == "hello world test"
        assert parsed["round"] == 3
        assert isinstance(parsed["word_count"], int)

    def test_word_count_matches_content(self) -> None:
        agent = make_agent()
        msg = agent.send_message("one two three four five", ping_num=1)
        assert msg.word_count == 5


class TestReceiveMessage:
    def test_receive_debate_message_directly(self) -> None:
        agent = make_agent()
        incoming = DebateMessage(type="argument", round=1, sender="con", content="Office is better", word_count=3)
        agent.receive_message(incoming)
        assert agent._last_received is incoming  # noqa: SLF001

    def test_receive_message_parses_dict(self) -> None:
        agent = make_agent()
        data = {
            "type": "argument", "round": 2, "sender": "con",
            "content": "Office work fosters collaboration",
            "timestamp": "2026-01-01T00:00:00+00:00", "word_count": 5,
        }
        agent.receive_message(data)
        assert agent._last_received is not None  # noqa: SLF001
        assert agent._last_received.sender == "con"  # noqa: SLF001
        assert agent._last_received.content == "Office work fosters collaboration"  # noqa: SLF001

    def test_last_received_starts_as_none(self) -> None:
        agent = make_agent()
        assert agent._last_received is None  # noqa: SLF001
