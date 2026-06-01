"""Unit tests for BaseAgent — TDD Red phase written before implementation."""

from __future__ import annotations

import json
import time as _time
from unittest.mock import MagicMock

import pytest

from debate.agents.base_agent import BaseAgent, DebateMessage

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeCfg:
    """Minimal stand-in for ConfigManager — returns plain dicts."""

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.setup = {
            "debate": {
                "model": "claude-haiku-4-5",
                "timeout_seconds": timeout_seconds,
                "word_limit": 150,
                "rounds": 10,
            }
        }
        self.rate_limits = {
            "anthropic": {"max_tokens_per_call": 500},
            "tavily": {"max_results_per_search": 3},
        }


class ConcreteAgent(BaseAgent):
    """Minimal concrete implementation for testing the abstract base."""

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        text = self._call_llm(f"Respond to: {opponent_msg.content}")
        return self.send_message(text, ping_num=opponent_msg.round + 1)

    def get_skill_prompt(self) -> str:
        return "I am a test agent."


def _make_mock_response(text: str = "test response") -> MagicMock:
    resp = MagicMock()
    resp.usage.input_tokens = 10
    resp.usage.output_tokens = 20
    resp.content = [MagicMock(text=text)]
    return resp


def _make_agent(
    role: str = "pro",
    gatekeeper: MagicMock | None = None,
    timeout_seconds: float = 5.0,
    tavily: MagicMock | None = None,
) -> ConcreteAgent:
    if gatekeeper is None:
        gatekeeper = MagicMock()
        gatekeeper.call.return_value = _make_mock_response()
    return ConcreteAgent(
        role=role,
        config_manager=FakeCfg(timeout_seconds),
        gatekeeper=gatekeeper,
        tavily=tavily,
    )


# ---------------------------------------------------------------------------
# 1. Agent initializes with correct config
# ---------------------------------------------------------------------------
class TestInitialization:
    def test_initializes_with_correct_config(self) -> None:
        """Agent must load role, model, timeout, word_limit, and max_tokens from config."""
        agent = _make_agent(role="pro")
        assert agent._role == "pro"  # noqa: SLF001
        assert agent._model == "claude-haiku-4-5"  # noqa: SLF001
        assert agent._timeout == 5.0  # noqa: SLF001
        assert agent._word_limit == 150  # noqa: SLF001
        assert agent._max_tokens == 500  # noqa: SLF001

    def test_gatekeeper_stored_on_agent(self) -> None:
        """Gatekeeper must be accessible as an attribute after init."""
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        agent = _make_agent(gatekeeper=gk)
        assert agent._gatekeeper is gk  # noqa: SLF001


# ---------------------------------------------------------------------------
# 2. send_message() produces valid JSON
# ---------------------------------------------------------------------------
class TestSendMessage:
    def test_send_message_returns_debate_message(self) -> None:
        """send_message must return a DebateMessage with the correct fields."""
        agent = _make_agent()
        msg = agent.send_message("Remote work improves productivity", ping_num=2)
        assert isinstance(msg, DebateMessage)
        assert msg.sender == "pro"
        assert msg.type == "argument"
        assert msg.round == 2
        assert msg.content == "Remote work improves productivity"

    def test_send_message_produces_valid_json(self) -> None:
        """The DebateMessage returned by send_message must be JSON-serializable."""
        agent = _make_agent()
        msg = agent.send_message("hello world test", ping_num=3)
        raw = msg.to_json()
        parsed = json.loads(raw)
        assert parsed["type"] == "argument"
        assert parsed["sender"] == "pro"
        assert parsed["content"] == "hello world test"
        assert parsed["round"] == 3
        assert isinstance(parsed["word_count"], int)

    def test_word_count_matches_content(self) -> None:
        """word_count in the returned message must equal the number of words."""
        agent = _make_agent()
        msg = agent.send_message("one two three four five", ping_num=1)
        assert msg.word_count == 5


# ---------------------------------------------------------------------------
# 3. receive_message() parses JSON correctly
# ---------------------------------------------------------------------------
class TestReceiveMessage:
    def test_receive_debate_message_directly(self) -> None:
        """receive_message must store a DebateMessage object directly."""
        agent = _make_agent()
        incoming = DebateMessage(
            type="argument", round=1, sender="con", content="Office is better", word_count=3
        )
        agent.receive_message(incoming)
        assert agent._last_received is incoming  # noqa: SLF001

    def test_receive_message_parses_dict(self) -> None:
        """receive_message must convert a plain dict (parsed JSON) into a DebateMessage."""
        agent = _make_agent()
        data = {
            "type": "argument",
            "round": 2,
            "sender": "con",
            "content": "Office work fosters collaboration",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "word_count": 5,
        }
        agent.receive_message(data)
        assert agent._last_received is not None  # noqa: SLF001
        assert agent._last_received.sender == "con"  # noqa: SLF001
        assert agent._last_received.content == "Office work fosters collaboration"  # noqa: SLF001

    def test_last_received_starts_as_none(self) -> None:
        """Before any message is received, _last_received must be None."""
        agent = _make_agent()
        assert agent._last_received is None  # noqa: SLF001


# ---------------------------------------------------------------------------
# 4. Timeout raises TimeoutError with clear message
# ---------------------------------------------------------------------------
class TestTimeout:
    def test_timeout_raises_timeout_error(self) -> None:
        """_call_llm must raise TimeoutError when gatekeeper takes longer than timeout."""

        def slow_call(**kwargs):
            _time.sleep(0.1)  # 100 ms — far longer than 1 ms timeout
            return _make_mock_response()

        gk = MagicMock()
        gk.call.side_effect = slow_call

        agent = _make_agent(gatekeeper=gk, timeout_seconds=0.001)
        with pytest.raises(TimeoutError, match="timed out"):
            agent._call_llm("test prompt")  # noqa: SLF001


# ---------------------------------------------------------------------------
# 5. Web search returns structured results
# ---------------------------------------------------------------------------
class TestWebSearch:
    def test_search_web_returns_structured_results(self) -> None:
        """search_web must map Tavily results to {title, url, snippet} dicts."""
        mock_tavily = MagicMock()
        mock_tavily.search.return_value = {
            "results": [
                {
                    "title": "Remote Work Study",
                    "url": "https://example.com",
                    "content": "Remote work boosts productivity.",
                },
                {
                    "title": "Office Research",
                    "url": "https://research.org",
                    "content": "In-person teams collaborate better.",
                },
            ]
        }
        agent = _make_agent(tavily=mock_tavily)
        results = agent.search_web("remote work productivity")
        assert len(results) == 2
        assert results[0] == {
            "title": "Remote Work Study",
            "url": "https://example.com",
            "snippet": "Remote work boosts productivity.",
        }

    def test_search_web_returns_empty_without_tavily(self) -> None:
        """search_web must return [] when no Tavily client is injected."""
        agent = _make_agent(tavily=None)
        assert agent.search_web("anything") == []

    def test_search_web_passes_correct_query(self) -> None:
        """search_web must forward the query string and max_results to Tavily."""
        mock_tavily = MagicMock()
        mock_tavily.search.return_value = {"results": []}
        agent = _make_agent(tavily=mock_tavily)
        agent.search_web("remote work statistics")
        mock_tavily.search.assert_called_once_with(
            query="remote work statistics", max_results=3
        )


# ---------------------------------------------------------------------------
# 6. All LLM calls go through Gatekeeper
# ---------------------------------------------------------------------------
class TestGatekeeperEnforcement:
    def test_llm_calls_go_through_gatekeeper(self) -> None:
        """_call_llm must invoke gatekeeper.call, not any direct Anthropic client."""
        gk = MagicMock()
        gk.call.return_value = _make_mock_response("gatekeeper response")
        agent = _make_agent(gatekeeper=gk)
        result = agent._call_llm("test prompt")  # noqa: SLF001
        gk.call.assert_called_once()
        assert result == "gatekeeper response"

    def test_gatekeeper_receives_model_from_config(self) -> None:
        """gatekeeper.call must be called with the model specified in config."""
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        agent = _make_agent(gatekeeper=gk)
        agent._call_llm("hello")  # noqa: SLF001
        assert gk.call.call_args.kwargs["model"] == "claude-haiku-4-5"

    def test_gatekeeper_receives_prompt_as_user_message(self) -> None:
        """gatekeeper.call must receive the prompt wrapped in a user role message."""
        gk = MagicMock()
        gk.call.return_value = _make_mock_response()
        agent = _make_agent(gatekeeper=gk)
        agent._call_llm("my specific prompt")  # noqa: SLF001
        messages = gk.call.call_args.kwargs["messages"]
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "my specific prompt"


# ---------------------------------------------------------------------------
# 7. Direct API calls raise an error
# ---------------------------------------------------------------------------
class TestNoDirectApiAccess:
    def test_no_raw_anthropic_client_attribute(self) -> None:
        """BaseAgent must not store a raw Anthropic client — all calls via gatekeeper."""
        agent = _make_agent()
        assert not hasattr(agent, "_client")
        assert not hasattr(agent, "_anthropic")
        assert not hasattr(agent, "_anthropic_client")

    def test_cannot_instantiate_base_agent_directly(self) -> None:
        """BaseAgent is abstract — direct instantiation must raise TypeError."""
        with pytest.raises(TypeError):
            BaseAgent(  # type: ignore[abstract]
                role="pro",
                config_manager=FakeCfg(),
                gatekeeper=MagicMock(),
            )
