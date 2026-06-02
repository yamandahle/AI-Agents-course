"""Shared helpers for BaseAgent unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate.agents.base_agent import BaseAgent, DebateMessage


class FakeCfg:
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


def make_mock_response(text: str = "test response") -> MagicMock:
    resp = MagicMock()
    resp.usage.input_tokens = 10
    resp.usage.output_tokens = 20
    resp.content = [MagicMock(text=text)]
    return resp


def make_agent(
    role: str = "pro",
    gatekeeper: MagicMock | None = None,
    timeout_seconds: float = 5.0,
    tavily: MagicMock | None = None,
) -> ConcreteAgent:
    if gatekeeper is None:
        gatekeeper = MagicMock()
        gatekeeper.call.return_value = make_mock_response()
    return ConcreteAgent(
        role=role,
        config_manager=FakeCfg(timeout_seconds),
        gatekeeper=gatekeeper,
        tavily=tavily,
    )
