"""BaseAgent — abstract foundation for all debate agents.

Enforces that every LLM call flows through ApiGatekeeper. Provides shared
behaviour: message creation, message receipt, web search, and timed LLM calls.
Concrete subclasses implement generate_argument() and get_skill_prompt().
"""

from __future__ import annotations

import abc
import dataclasses
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Message schema — shared by all agents and the SDK
# ---------------------------------------------------------------------------

@dataclass
class DebateMessage:
    """Structured message exchanged between debate agents via IPC queues."""

    type: str
    round: int
    sender: str
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )
    word_count: int = 0

    def to_json(self) -> str:
        """Serialise to a JSON string suitable for queue transport."""
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DebateMessage:
        """Deserialise from a plain dict (e.g. after json.loads on a queue message)."""
        return cls(
            type=data["type"],
            round=data["round"],
            sender=data["sender"],
            content=data["content"],
            timestamp=data.get("timestamp", datetime.now(tz=timezone.utc).isoformat()),
            word_count=data.get("word_count", 0),
        )


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class BaseAgent(abc.ABC):
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
        self._max_tokens: int = limits["anthropic"]["max_tokens_per_call"]
        self._max_results: int = limits["tavily"]["max_results_per_search"]

        self._gatekeeper = gatekeeper
        self._logger = logger
        self._tavily = tavily

        self._last_received: DebateMessage | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def send_message(self, content: str, ping_num: int) -> DebateMessage:
        """Wrap content in a DebateMessage and log the event."""
        word_count = len(content.split())
        msg = DebateMessage(
            type="argument",
            round=ping_num,
            sender=self._role,
            content=content,
            word_count=word_count,
        )
        if self._logger is not None:
            self._logger.info(
                self._role, "argument", {"round": ping_num, "word_count": word_count}
            )
        return msg

    def receive_message(self, message: DebateMessage | dict[str, Any]) -> None:
        """Store the incoming message, converting from dict if necessary."""
        if isinstance(message, dict):
            self._last_received = DebateMessage.from_dict(message)
        else:
            self._last_received = message

    def search_web(self, query: str) -> list[dict[str, str]]:
        """Run a Tavily search and return [{title, url, snippet}] results."""
        if self._tavily is None:
            return []
        raw = self._tavily.search(query=query, max_results=self._max_results)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
            }
            for r in raw.get("results", [])
        ]

    # ------------------------------------------------------------------
    # Abstract interface — concrete agents must implement these
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        """Generate a rebuttal argument in response to the opponent's message."""

    @abc.abstractmethod
    def get_skill_prompt(self) -> str:
        """Return the agent-specific system prompt describing its debate style."""

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str) -> str:
        """Send prompt through the Gatekeeper with a hard timeout.

        Raises TimeoutError if the Gatekeeper does not respond within
        timeout_seconds from config. Direct access to any API client is
        intentionally absent — all calls must flow through self._gatekeeper.
        """
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            self._gatekeeper.call,
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self._max_tokens,
        )
        try:
            response = future.result(timeout=self._timeout)
            return response.content[0].text
        except FutureTimeoutError:
            raise TimeoutError(
                f"LLM call timed out after {self._timeout}s for role={self._role}"
            ) from None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
