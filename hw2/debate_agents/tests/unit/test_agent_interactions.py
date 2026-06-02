"""Tests for distinct skills, opponent references, and web search integration."""

from __future__ import annotations

from unittest.mock import MagicMock

from agent_test_helpers import FakeCfg, make_con, make_mock_response, make_pro, opponent_msg

from debate.agents.con_agent import ConAgent
from debate.agents.pro_agent import ProAgent


class TestDistinctSkills:
    def test_skill_prompts_are_different(self) -> None:
        pro, _, _ = make_pro()
        con, _, _ = make_con()
        assert pro.get_skill_prompt() != con.get_skill_prompt()

    def test_pro_and_con_search_in_opposite_directions(self) -> None:
        pro, _, pro_tavily = make_pro()
        con, _, con_tavily = make_con()
        msg = opponent_msg()
        pro.generate_argument(msg)
        con.generate_argument(msg)
        assert pro_tavily.search.call_args.kwargs["query"] != con_tavily.search.call_args.kwargs["query"]


class TestOpponentReference:
    def test_pro_prompt_contains_opponent_content(self) -> None:
        pro, gk, _ = make_pro()
        msg = opponent_msg(content="Office workers collaborate 40% better on complex tasks.")
        pro.generate_argument(msg)
        user_content = gk.call.call_args.kwargs["messages"][0]["content"]
        assert "Office workers collaborate 40% better on complex tasks." in user_content

    def test_con_prompt_contains_opponent_content(self) -> None:
        con, gk, _ = make_con()
        msg = opponent_msg(content="Stanford study shows 13% productivity gain from remote work.", sender="pro")
        con.generate_argument(msg)
        user_content = gk.call.call_args.kwargs["messages"][0]["content"]
        assert "Stanford study shows 13% productivity gain from remote work." in user_content


class TestWebSearch:
    def test_pro_calls_web_search_during_argument(self) -> None:
        pro, _, tavily = make_pro()
        pro.generate_argument(opponent_msg())
        tavily.search.assert_called_once()

    def test_con_calls_web_search_during_argument(self) -> None:
        con, _, tavily = make_con()
        con.generate_argument(opponent_msg())
        tavily.search.assert_called_once()

    def test_pro_search_result_included_in_llm_prompt(self) -> None:
        snippet = "Studies show remote workers save 2 hours per day commuting."
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        tavily = MagicMock()
        tavily.search.return_value = {"results": [{"title": "Study", "url": "https://ex.com", "content": snippet}]}
        pro = ProAgent(role="pro", config_manager=FakeCfg(), gatekeeper=gk, tavily=tavily)
        pro.generate_argument(opponent_msg())
        assert snippet in gk.call.call_args.kwargs["messages"][0]["content"]

    def test_con_search_result_included_in_llm_prompt(self) -> None:
        snippet = "In-person brainstorming produces 42% more creative solutions."
        gk = MagicMock()
        gk.call.return_value = make_mock_response()
        tavily = MagicMock()
        tavily.search.return_value = {"results": [{"title": "Research", "url": "https://r.com", "content": snippet}]}
        con = ConAgent(role="con", config_manager=FakeCfg(), gatekeeper=gk, tavily=tavily)
        con.generate_argument(opponent_msg())
        assert snippet in gk.call.call_args.kwargs["messages"][0]["content"]
