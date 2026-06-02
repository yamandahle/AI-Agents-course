"""Tests for BaseAgent timeout, web search, gatekeeper enforcement, and no-bypass rules."""

from __future__ import annotations

import time as _time
from unittest.mock import MagicMock

import pytest
from base_agent_test_helpers import FakeCfg, make_agent, make_mock_response

from debate.agents.base_agent import BaseAgent


class TestTimeout:
    def test_timeout_raises_timeout_error(self) -> None:
        def slow_call(**kwargs):
            _time.sleep(0.1)
            return make_mock_response()

        gk = MagicMock()
        gk.call.side_effect = slow_call
        agent = make_agent(gatekeeper=gk, timeout_seconds=0.001)
        with pytest.raises(TimeoutError, match="timed out"):
            agent._call_llm("test prompt")  # noqa: SLF001


class TestWebSearch:
    def test_search_web_returns_structured_results(self) -> None:
        mock_tavily = MagicMock()
        mock_tavily.search.return_value = {
            "results": [
                {"title": "Remote Work Study", "url": "https://example.com",
                 "content": "Remote work boosts productivity."},
                {"title": "Office Research", "url": "https://research.org",
                 "content": "In-person teams collaborate better."},
            ]
        }
        agent = make_agent(tavily=mock_tavily)
        results = agent.search_web("remote work productivity")
        assert len(results) == 2
        assert results[0] == {
            "title": "Remote Work Study", "url": "https://example.com",
            "snippet": "Remote work boosts productivity.",
        }

    def test_search_web_returns_empty_without_tavily(self) -> None:
        agent = make_agent(tavily=None)
        assert agent.search_web("anything") == []

    def test_search_web_passes_correct_query(self) -> None:
        mock_tavily = MagicMock()
        mock_tavily.search.return_value = {"results": []}
        agent = make_agent(tavily=mock_tavily)
        agent.search_web("remote work statistics")
        mock_tavily.search.assert_called_once_with(query="remote work statistics", max_results=3)


class TestGatekeeperEnforcement:
    def test_llm_calls_go_through_gatekeeper(self) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response("gatekeeper response")
        agent = make_agent(gatekeeper=gk)
        result = agent._call_llm("test prompt")  # noqa: SLF001
        gk.call.assert_called_once()
        assert result == "gatekeeper response"

    def test_gatekeeper_receives_model_from_config(self) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        agent = make_agent(gatekeeper=gk)
        agent._call_llm("hello")  # noqa: SLF001
        assert gk.call.call_args.kwargs["model"] == "claude-haiku-4-5"

    def test_gatekeeper_receives_prompt_as_user_message(self) -> None:
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        agent = make_agent(gatekeeper=gk)
        agent._call_llm("my specific prompt")  # noqa: SLF001
        messages = gk.call.call_args.kwargs["messages"]
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "my specific prompt"


class TestNoDirectApiAccess:
    def test_no_raw_anthropic_client_attribute(self) -> None:
        agent = make_agent()
        assert not hasattr(agent, "_client")
        assert not hasattr(agent, "_anthropic")
        assert not hasattr(agent, "_anthropic_client")

    def test_cannot_instantiate_base_agent_directly(self) -> None:
        with pytest.raises(TypeError):
            BaseAgent(  # type: ignore[abstract]
                role="pro", config_manager=FakeCfg(), gatekeeper=MagicMock(),
            )
