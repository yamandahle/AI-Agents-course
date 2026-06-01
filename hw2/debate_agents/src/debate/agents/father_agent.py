"""FatherAgent — neutral moderator that routes, detects violations, and scores the debate."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from debate.agents.base_agent import BaseAgent, DebateMessage
from debate.agents.father_scoring import ArgumentScorer, DebateResult

_AGREEMENT_PHRASES: tuple[str, ...] = (
    "good point", "i agree", "you are right", "that is correct",
    "fair enough", "i concede", "you're right", "that's true",
    "valid point", "i understand your concern",
)

_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "must", "can", "could", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "that", "this",
        "it", "its", "and", "or", "but", "not", "so", "if", "than", "then",
    }
)

_OnEvent = Callable[..., None] | None


class FatherAgent(BaseAgent):
    """Debate moderator: routes turns, enforces rules, tracks context, produces verdict."""

    def __init__(
        self, role: str, config_manager: Any, gatekeeper: Any,
        logger: Any = None, tavily: Any = None,
    ) -> None:
        super().__init__(role, config_manager, gatekeeper, logger, tavily)
        debate_cfg = config_manager.setup["debate"]
        self._rounds: int = debate_cfg["rounds"]
        self._summarize_after: int = debate_cfg["context_summarize_after_round"]
        self._token_multiplier: float = debate_cfg["token_estimate_multiplier"]
        self._scorer = ArgumentScorer()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run_debate(
        self, topic: str, pro_agent: Any, con_agent: Any, on_event: _OnEvent = None,
    ) -> DebateResult:
        """Run the full debate: route turns, detect violations, track context."""
        transcript: list[DebateMessage] = []
        pro_history: list[DebateMessage] = []
        con_history: list[DebateMessage] = []
        interventions = 0
        context_tokens = 0
        current_msg = DebateMessage(type="argument", round=0, sender="con", content=topic)

        for rnd in range(1, self._rounds + 1):
            self._fire(on_event, "round_start", {"round": rnd, "total": self._rounds})

            self._fire(on_event, "pro_searching", {})
            pro_msg = pro_agent.generate_argument(current_msg)
            self._fire(on_event, "pro_argument", {"content": pro_msg.content})
            self._fire(on_event, "father_validate", {"agent": "pro", "ok": True})
            pro_msg, n = self._check_and_intervene(
                pro_msg, pro_agent, "pro", current_msg, pro_history, on_event,
            )
            interventions += n
            pro_history.append(pro_msg)
            transcript.append(pro_msg)
            self._fire(on_event, "father_route", {"to": "con"})

            self._fire(on_event, "con_searching", {})
            con_msg = con_agent.generate_argument(pro_msg)
            self._fire(on_event, "con_argument", {"content": con_msg.content})
            self._fire(on_event, "father_validate", {"agent": "con", "ok": True})
            con_msg, n = self._check_and_intervene(
                con_msg, con_agent, "con", pro_msg, con_history, on_event,
            )
            interventions += n
            con_history.append(con_msg)
            transcript.append(con_msg)

            round_tokens = round(
                (pro_msg.word_count + con_msg.word_count) * self._token_multiplier
            )
            context_tokens += round_tokens
            self._fire(on_event, "context_update", {"round": rnd, "new_tokens": round_tokens, "total": context_tokens})

            if self._logger is not None:
                self._logger.info("father", "context_update", {"round": rnd, "new_tokens": round_tokens, "total": context_tokens})
                if rnd == self._summarize_after:
                    self._logger.info("father", "context_compact", {"rounds_summarized": f"1-{rnd - 1}", "tokens_saved": context_tokens // 2})

            if rnd == self._summarize_after:
                self._fire(on_event, "context_compact", {"saved": context_tokens // 2})

            current_msg = con_msg

        result = self._produce_verdict(pro_history, con_history, transcript, interventions, context_tokens)
        self._fire(on_event, "verdict", {"result": result})
        return result

    def get_skill_prompt(self) -> str:
        return (Path(self._skills_path) / "father_skill.md").read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        return self.send_message("[ROUTE]", ping_num=opponent_msg.round)

    # ------------------------------------------------------------------
    # Detection and intervention
    # ------------------------------------------------------------------

    def _detect_agreement(self, message: DebateMessage) -> bool:
        content_lower = message.content.lower()
        return any(phrase in content_lower for phrase in _AGREEMENT_PHRASES)

    def _detect_repetition(self, message: DebateMessage, history: list[DebateMessage]) -> bool:
        if not history:
            return False
        msg_words = {w.strip(".,!?;:") for w in message.content.lower().split()} - _STOPWORDS
        if not msg_words:
            return False
        for prev in history[-3:]:
            prev_words = {w.strip(".,!?;:") for w in prev.content.lower().split()} - _STOPWORDS
            if not prev_words:
                continue
            intersection = len(msg_words & prev_words)
            union = len(msg_words | prev_words)
            if union > 0 and intersection / union > 0.7:
                return True
        return False

    def _check_and_intervene(
        self,
        msg: DebateMessage,
        agent: Any,
        agent_name: str,
        opponent_msg: DebateMessage,
        history: list[DebateMessage],
        on_event: _OnEvent = None,
    ) -> tuple[DebateMessage, int]:
        if self._detect_agreement(msg):
            self._fire(on_event, "father_check", {"agent": agent_name, "check": "agreement", "ok": False})
            self._fire(on_event, "intervention", {"agent": agent_name, "reason": "agreement"})
            return self._intervene(agent, "agreement", opponent_msg), 1
        self._fire(on_event, "father_check", {"agent": agent_name, "check": "agreement", "ok": True})
        if self._detect_repetition(msg, history):
            self._fire(on_event, "father_check", {"agent": agent_name, "check": "repetition", "ok": False})
            self._fire(on_event, "intervention", {"agent": agent_name, "reason": "repetition"})
            return self._intervene(agent, "repetition", opponent_msg), 1
        self._fire(on_event, "father_check", {"agent": agent_name, "check": "repetition", "ok": True})
        return msg, 0

    def _intervene(self, agent: Any, reason: str, opponent_msg: DebateMessage) -> DebateMessage:
        notice = DebateMessage(
            type="intervention", round=opponent_msg.round, sender="father",
            content=f"INTERVENTION ({reason}): Rewrite with a stronger, distinct argument.",
        )
        agent.receive_message(notice)
        if self._logger is not None:
            self._logger.info("father", "intervention", {"reason": reason, "round": opponent_msg.round})
        return agent.generate_argument(opponent_msg)

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------

    def _produce_verdict(
        self,
        pro_history: list[DebateMessage],
        con_history: list[DebateMessage],
        transcript: list[DebateMessage],
        interventions: int,
        context_tokens: int,
    ) -> DebateResult:
        pro_raw = self._scorer.score(pro_history, self._word_limit)
        con_raw = self._scorer.score(con_history, self._word_limit)
        total = pro_raw + con_raw
        if total == 0:
            pro_pct, con_pct = 60.0, 40.0
        else:
            pro_pct = round(pro_raw / total * 100, 1)
            con_pct = round(100.0 - pro_pct, 1)
        if abs(pro_pct - con_pct) < 1.0:
            pro_pct = min(100.0, pro_pct + 1.0)
            con_pct = max(0.0, con_pct - 1.0)
        winner = "pro" if pro_pct >= con_pct else "con"
        if max(pro_pct, con_pct) < 60.0:
            pro_pct, con_pct = (60.0, 40.0) if winner == "pro" else (40.0, 60.0)
        return DebateResult(
            winner=winner, pro_score=pro_pct, con_score=con_pct,
            total_interventions=interventions, rounds_completed=len(pro_history),
            transcript=transcript, context_tokens=context_tokens,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fire(self, on_event: _OnEvent, event: str, data: dict[str, Any]) -> None:
        if on_event is not None:
            on_event(event, data)
