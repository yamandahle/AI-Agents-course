"""Shared helpers for ProAgent and ConAgent unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate.agents.base_agent import DebateMessage
from debate.agents.con_agent import ConAgent
from debate.agents.pro_agent import ProAgent


class FakeCfg:
    def __init__(self, word_limit: int = 150) -> None:
        self.setup = {
            "debate": {
                "model": "claude-haiku-4-5",
                "timeout_seconds": 5.0,
                "word_limit": word_limit,
                "rounds": 10,
            }
        }
        self.rate_limits = {
            "anthropic": {"max_tokens_per_call": 500},
            "tavily": {"max_results_per_search": 3},
        }


def make_mock_response(text: str = "This is a test argument.") -> MagicMock:
    resp = MagicMock()
    resp.usage.input_tokens = 10
    resp.usage.output_tokens = 20
    resp.content = [MagicMock(text=text)]
    return resp


def make_mock_tavily(snippet: str = "Remote work increases productivity by 13%.") -> MagicMock:
    tavily = MagicMock()
    tavily.search.return_value = {
        "results": [{"title": "Study 1", "url": "https://study1.com", "content": snippet}]
    }
    return tavily


def make_pro(word_limit: int = 150, response_text: str = "Remote work is clearly superior.") -> tuple[ProAgent, MagicMock, MagicMock]:
    gk = MagicMock()
    gk.call.return_value = make_mock_response(response_text)
    tavily = make_mock_tavily()
    agent = ProAgent(role="pro", config_manager=FakeCfg(word_limit), gatekeeper=gk, tavily=tavily)
    return agent, gk, tavily


def make_con(word_limit: int = 150, response_text: str = "Office work is clearly superior.") -> tuple[ConAgent, MagicMock, MagicMock]:
    gk = MagicMock()
    gk.call.return_value = make_mock_response(response_text)
    tavily = make_mock_tavily("Office collaboration improves output by 20%.")
    agent = ConAgent(role="con", config_manager=FakeCfg(word_limit), gatekeeper=gk, tavily=tavily)
    return agent, gk, tavily


def opponent_msg(content: str = "Office work builds team culture.", round_num: int = 1, sender: str = "con") -> DebateMessage:
    return DebateMessage(type="argument", round=round_num, sender=sender, content=content)
