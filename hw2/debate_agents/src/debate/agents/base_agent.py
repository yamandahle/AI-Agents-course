"""BaseAgent — abstract foundation for all debate agents."""

from __future__ import annotations

import abc
from typing import Any

from debate.agents.agent_mixin import _AgentMixin
from debate.agents.models import DebateMessage

__all__ = ["BaseAgent", "DebateMessage"]


class BaseAgent(abc.ABC, _AgentMixin):
    """Abstract agent — subclasses must implement generate_argument and get_skill_prompt."""

    def __init__(
        self,
        role: str,
        config_manager: Any,
        gatekeeper: Any,
        logger: Any = None,
        tavily: Any = None,
    ) -> None:
        setup = config_manager.setup
        limits = config_manager.rate_limits
        self._role: str = role
        self._model: str = setup["debate"]["model"]
        self._timeout: float = setup["debate"]["timeout_seconds"]
        self._word_limit: int = setup["debate"]["word_limit"]
        self._skills_path: str = setup["debate"].get("skills_path", "src/debate/skills/")
        self._max_tokens: int = limits["anthropic"]["max_tokens_per_call"]
        self._max_results: int = limits["tavily"]["max_results_per_search"]
        self._gatekeeper = gatekeeper
        self._logger = logger
        self._tavily = tavily
        self._last_received: DebateMessage | None = None

    def send_message(self, content: str, ping_num: int) -> DebateMessage:
        word_count = len(content.split())
        msg = DebateMessage(
            type="argument", round=ping_num, sender=self._role,
            content=content, word_count=word_count,
        )
        if self._logger is not None:
            self._logger.info(
                self._role, "argument", {"round": ping_num, "word_count": word_count}
            )
        return msg

    def receive_message(self, message: DebateMessage | dict[str, Any]) -> None:
        if isinstance(message, dict):
            self._last_received = DebateMessage.from_dict(message)
        else:
            self._last_received = message

    def search_web(self, query: str) -> list[dict[str, str]]:
        if self._tavily is None:
            return []
        raw = self._tavily.search(query=query, max_results=self._max_results)
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
            for r in raw.get("results", [])
        ]

    @abc.abstractmethod
    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Generate a rebuttal argument in response to the opponent's message."""

    @abc.abstractmethod
    def get_skill_prompt(self) -> str:
        """Return the agent-specific system prompt describing its debate style."""
