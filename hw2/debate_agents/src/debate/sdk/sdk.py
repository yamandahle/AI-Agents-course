"""DebateSDK — single entry point for all external consumers.

Contains no business logic. All operations delegate to domain services.
External callers interact only with this module — never with agents or
services directly.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from debate.agents.base_agent import DebateMessage
from debate.agents.father_scoring import DebateResult


class SessionNotFoundError(KeyError):
    """Raised when a session_id does not map to any known session."""


@dataclass
class DebateSession:
    """Represents one debate run — its state, transcript, and cost data."""

    session_id: str
    topic: str
    status: str
    config_path: str
    transcript: list[DebateMessage] = field(default_factory=list)
    cost_report: dict[str, Any] = field(default_factory=dict)
    result: DebateResult | None = None


def _config_dir_from_path(config_path: str) -> str:
    """Accept either a config directory or a path to a JSON file inside it."""
    path = Path(config_path)
    if path.suffix.lower() == ".json":
        return str(path.parent)
    return config_path


class DebateSDK:
    """Stateful SDK instance — holds all active and completed sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, DebateSession] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start_debate(self, topic: str, config_path: str) -> DebateSession:
        """Create and register a new debate session, returning it immediately."""
        session = DebateSession(
            session_id=str(uuid.uuid4()),
            topic=topic,
            status="running",
            config_path=config_path,
        )
        self._sessions[session.session_id] = session
        return session

    def execute_debate(
        self,
        session_id: str,
        on_event: Callable[..., None] | None = None,
    ) -> DebateSession:
        """Run the debate for an existing session via DebateOrchestrator.

        Blocks until the debate completes, then updates the session with results.
        """
        from debate.services.debate_orchestrator import DebateOrchestrator

        session = self._get(session_id)
        config_dir = _config_dir_from_path(session.config_path)
        orchestrator = DebateOrchestrator(config_dir=config_dir)
        result = orchestrator.run(session.topic, on_event=on_event)

        session.status = "completed"
        session.transcript = list(result.transcript)
        session.cost_report = {"entries": orchestrator.get_cost_breakdown()}
        session.result = result
        return session

    def get_status(self, session_id: str) -> dict[str, Any]:
        """Return a dict snapshot of session status fields."""
        session = self._get(session_id)
        return {
            "session_id": session.session_id,
            "status": session.status,
            "topic": session.topic,
        }

    def get_transcript(self, session_id: str) -> list[DebateMessage]:
        """Return a copy of the debate transcript so callers cannot mutate state."""
        return list(self._get(session_id).transcript)

    def get_cost_report(self, session_id: str) -> dict[str, Any]:
        """Return a copy of the session cost report."""
        return dict(self._get(session_id).cost_report)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get(self, session_id: str) -> DebateSession:
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"No session found for id={session_id!r}")
        return self._sessions[session_id]


# ---------------------------------------------------------------------------
# Module-level convenience functions backed by a default SDK instance.
# External consumers can use these without managing a DebateSDK object.
# ---------------------------------------------------------------------------

_default = DebateSDK()


def start_debate(topic: str, config_path: str) -> DebateSession:
    return _default.start_debate(topic, config_path)


def execute_debate(
    session_id: str, on_event: Callable[..., None] | None = None
) -> DebateSession:
    return _default.execute_debate(session_id, on_event=on_event)


def get_status(session_id: str) -> dict[str, Any]:
    return _default.get_status(session_id)


def get_transcript(session_id: str) -> list[DebateMessage]:
    return _default.get_transcript(session_id)


def get_cost_report(session_id: str) -> dict[str, Any]:
    return _default.get_cost_report(session_id)
