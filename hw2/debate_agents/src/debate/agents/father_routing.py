"""_RoutingMixin — intervention and coaching helpers for FatherAgent."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from debate.agents.father_checks import detect_agreement, detect_repetition
from debate.agents.models import DebateMessage

_OnEvent = Callable[..., None] | None


class _RoutingMixin:
    """Provides _check_and_intervene, _intervene, and _coach for FatherAgent."""

    def _check_and_intervene(
        self,
        msg: DebateMessage,
        agent: Any,
        agent_name: str,
        opponent_msg: DebateMessage,
        history: list[DebateMessage],
        on_event: _OnEvent = None,
    ) -> tuple[DebateMessage, int]:
        if detect_agreement(msg):
            self._fire(on_event, "father_check", {"agent": agent_name, "check": "agreement", "ok": False})
            self._fire(on_event, "intervention", {"agent": agent_name, "reason": "agreement"})
            return self._intervene(agent, "agreement", opponent_msg), 1
        self._fire(on_event, "father_check", {"agent": agent_name, "check": "agreement", "ok": True})
        if detect_repetition(msg, history):
            self._fire(on_event, "father_check", {"agent": agent_name, "check": "repetition", "ok": False})
            self._fire(on_event, "intervention", {"agent": agent_name, "reason": "repetition"})
            return self._intervene(agent, "repetition", opponent_msg), 1
        self._fire(on_event, "father_check", {"agent": agent_name, "check": "repetition", "ok": True})
        return msg, 0

    def _intervene(self, agent: Any, reason: str, opponent_msg: DebateMessage) -> DebateMessage:
        if reason == "agreement":
            instruction = (
                "INTERVENTION: You agreed with your opponent — that is forbidden. "
                "Rewrite. Attack their claim directly. Introduce a brand-new concept "
                "you have not used in any previous round."
            )
        else:
            instruction = (
                "INTERVENTION: You repeated a concept already argued. "
                "Pick a completely different angle you have NOT raised before. "
                "Also rebut your opponent's last specific claim in one sentence."
            )
        notice = DebateMessage(
            type="intervention", round=opponent_msg.round, sender="father",
            content=instruction,
        )
        agent.receive_message(notice)
        if self._logger is not None:
            self._logger.info("father", "intervention", {"reason": reason, "round": opponent_msg.round})
        return agent.generate_argument(opponent_msg)

    def _coach(
        self, msg: DebateMessage, agent_name: str, seen_urls: set[str], on_event: _OnEvent,
    ) -> None:
        if msg.word_count < 50:
            self._fire(on_event, "father_coaching", {
                "agent": agent_name,
                "message": "Too short — you left your argument half-finished. Develop it more next round.",
            })
        url = msg.evidence_url.strip()
        if url and url in seen_urls:
            self._fire(on_event, "father_coaching", {
                "agent": agent_name,
                "message": "You reused that source. Find completely fresh evidence next round.",
            })
        if url:
            seen_urls.add(url)

    # Attributes provided by the host class
    _logger: Any

    def _fire(self, on_event: _OnEvent, event: str, data: dict[str, Any]) -> None:  # pragma: no cover
        raise NotImplementedError
