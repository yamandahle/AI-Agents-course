"""Shared helpers for FatherAgent unit tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from debate.agents.base_agent import DebateMessage
from debate.agents.father_agent import FatherAgent


class FakeCfg:
    def __init__(self, rounds: int = 3, summarize_after: int = 99, word_limit: int = 150) -> None:
        self.setup = {
            "debate": {
                "model": "claude-haiku-4-5",
                "timeout_seconds": 5.0,
                "word_limit": word_limit,
                "rounds": rounds,
                "max_restarts": 3,
                "watchdog_interval_seconds": 2,
                "context_summarize_after_round": summarize_after,
                "token_estimate_multiplier": 1.3,
                "skills_path": "src/debate/skills/",
            }
        }
        self.rate_limits = {
            "anthropic": {"max_tokens_per_call": 500},
            "tavily": {"max_results_per_search": 3},
        }


class MockAgent:
    def __init__(self, role: str, responses: list[str]) -> None:
        self._role = role
        self._responses = responses
        self._idx = 0
        self.received: list[DebateMessage] = []

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        text = self._responses[self._idx % len(self._responses)]
        self._idx += 1
        return DebateMessage(
            type="argument", round=opponent_msg.round + 1,
            sender=self._role, content=text, word_count=len(text.split()),
        )

    def receive_message(self, msg: DebateMessage) -> None:
        self.received.append(msg)


def make_father(rounds: int = 3, summarize_after: int = 99) -> FatherAgent:
    gk = MagicMock()
    logger = MagicMock()
    return FatherAgent(
        role="father",
        config_manager=FakeCfg(rounds=rounds, summarize_after=summarize_after),
        gatekeeper=gk,
        logger=logger,
    )


def std_responses() -> list[str]:
    return [
        "Commuting wastes two hours every day according to transportation studies.",
        "Home office setups improve focus and reduce distractions measurably.",
        "Companies report lower overhead costs when employees telecommute regularly.",
        "Research shows remote workers log more hours than office counterparts.",
        "Video conferencing technology bridges collaboration gaps between distributed teams.",
        "Urban congestion decreases substantially when fewer workers commute daily.",
        "Mental health improves when employees control their own workspace environment.",
        "Hiring globally expands talent pools beyond local geographic limitations.",
        "Synchronous collaboration thrives with proper async communication tools established.",
        "Energy consumption falls when office buildings operate at reduced capacity.",
    ]
