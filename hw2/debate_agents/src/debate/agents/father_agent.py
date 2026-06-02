"""FatherAgent — neutral moderator that routes, detects violations, and scores the debate."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import debate.agents.father_verdict as fv
from debate.agents.base_agent import BaseAgent, DebateMessage
from debate.agents.father_checks import detect_agreement, detect_contradiction, detect_repetition
from debate.agents.father_routing import _RoutingMixin
from debate.agents.father_scoring import ArgumentScorer, DebateResult

_OnEvent = Callable[..., None] | None


class FatherAgent(BaseAgent, _RoutingMixin):
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

    def get_skill_prompt(self) -> str:
        return (Path(self._skills_path) / "father_skill.md").read_text(encoding="utf-8")

    def generate_argument(self, opponent_msg: DebateMessage) -> DebateMessage:
        return self.send_message("[ROUTE]", ping_num=opponent_msg.round)

    def run_debate(
        self, topic: str, pro_agent: Any, con_agent: Any, on_event: _OnEvent = None,
    ) -> DebateResult:
        transcript: list[DebateMessage] = []
        pro_history: list[DebateMessage] = []
        con_history: list[DebateMessage] = []
        pro_concepts: list[str] = []
        con_concepts: list[str] = []
        pro_urls_seen: set[str] = set()
        con_urls_seen: set[str] = set()
        interventions = compactions = context_tokens = 0
        pro_contradictions = con_contradictions = pro_rounds_won = con_rounds_won = 0
        current_msg = DebateMessage(type="argument", round=0, sender="con", content=topic)

        for rnd in range(1, self._rounds + 1):
            self._fire(on_event, "round_start", {"round": rnd, "total": self._rounds})

            self._fire(on_event, "pro_searching", {})
            pro_msg = pro_agent.generate_argument(current_msg)
            self._fire(on_event, "pro_argument", {"content": pro_msg.content})
            self._fire(on_event, "father_validate", {"agent": "pro", "ok": True})
            pro_msg, n = self._check_and_intervene(pro_msg, pro_agent, "pro", current_msg, pro_history, on_event)
            interventions += n
            if pro_msg.concept and pro_msg.concept not in pro_concepts:
                pro_concepts.append(pro_msg.concept)
            if detect_contradiction(pro_msg, pro_history):
                pro_contradictions += 1
                self._fire(on_event, "father_check", {"agent": "pro", "check": "contradiction", "ok": False})
            self._coach(pro_msg, "pro", pro_urls_seen, on_event)
            pro_history.append(pro_msg)
            transcript.append(pro_msg)
            self._fire(on_event, "father_route", {"to": "con"})

            self._fire(on_event, "con_searching", {})
            con_msg = con_agent.generate_argument(pro_msg)
            self._fire(on_event, "con_argument", {"content": con_msg.content})
            self._fire(on_event, "father_validate", {"agent": "con", "ok": True})
            con_msg, n = self._check_and_intervene(con_msg, con_agent, "con", pro_msg, con_history, on_event)
            interventions += n
            if con_msg.concept and con_msg.concept not in con_concepts:
                con_concepts.append(con_msg.concept)
            if detect_contradiction(con_msg, con_history):
                con_contradictions += 1
                self._fire(on_event, "father_check", {"agent": "con", "check": "contradiction", "ok": False})
            self._coach(con_msg, "con", con_urls_seen, on_event)
            con_history.append(con_msg)
            transcript.append(con_msg)

            rnd_winner, rnd_reason = self._score_round(pro_msg, con_msg)
            if rnd_winner == "pro":
                pro_rounds_won += 1
            else:
                con_rounds_won += 1
            self._fire(on_event, "round_result", {"round": rnd, "winner": rnd_winner,
                "reason": rnd_reason, "pro_rounds_won": pro_rounds_won, "con_rounds_won": con_rounds_won})

            round_tokens = round((pro_msg.word_count + con_msg.word_count) * self._token_multiplier)
            context_tokens += round_tokens
            self._fire(on_event, "context_update", {"round": rnd, "new_tokens": round_tokens, "total": context_tokens})
            if self._logger is not None:
                self._logger.info("father", "context_update", {"round": rnd, "new_tokens": round_tokens, "total": context_tokens})

            if rnd % self._summarize_after == 0:
                compactions += 1
                summary = self._summarize_history(pro_history + con_history)
                if self._logger is not None:
                    self._logger.info("father", "context_compact", {"rounds_summarized": f"1-{rnd}", "tokens_saved": context_tokens // 2, "summary": summary})
                self._fire(on_event, "context_compact", {"saved": context_tokens // 2, "summary": summary})
            current_msg = con_msg

        result = self._produce_verdict(
            pro_history, con_history, transcript, interventions, context_tokens,
            pro_concepts=pro_concepts, con_concepts=con_concepts,
            pro_contradictions=pro_contradictions, con_contradictions=con_contradictions,
            compactions=compactions, pro_rounds_won=pro_rounds_won, con_rounds_won=con_rounds_won,
        )
        self._fire(on_event, "verdict", {"result": result})
        return result

    def _score_round(self, pro_msg: DebateMessage, con_msg: DebateMessage) -> tuple[str, str]:
        return fv.score_round(self._scorer, self._word_limit, pro_msg, con_msg)

    def _llm_evaluate(self, pro_history: list[DebateMessage], con_history: list[DebateMessage], pro_rounds_won: int, con_rounds_won: int) -> tuple[float | None, str]:
        return fv.llm_evaluate(self._call_llm, self.get_skill_prompt, pro_history, con_history, pro_rounds_won, con_rounds_won)

    def _produce_verdict(self, pro_history: list[DebateMessage], con_history: list[DebateMessage], transcript: list[DebateMessage], interventions: int, context_tokens: int, **kwargs: Any) -> DebateResult:
        return fv.produce_verdict(self._scorer, self._word_limit, self._llm_evaluate, pro_history, con_history, transcript, interventions, context_tokens, **kwargs)

    def _summarize_history(self, history: list[DebateMessage]) -> str:
        skill_path = Path(self._skills_path) / "summarize_skill.md"
        try:
            skill = skill_path.read_text(encoding="utf-8")
        except OSError:
            return "(summary unavailable)"
        transcript_text = "\n".join(f"Round {m.round} [{m.sender.upper()}]: {m.content}" for m in history)
        try:
            return self._call_llm(f"{skill}\n\nDEBATE HISTORY TO SUMMARIZE:\n{transcript_text}")
        except Exception:  # noqa: BLE001
            return "(summary unavailable)"

    def _fire(self, on_event: _OnEvent, event: str, data: dict[str, Any]) -> None:
        if on_event is not None:
            on_event(event, data)

    def _detect_agreement(self, message: DebateMessage) -> bool:
        return detect_agreement(message)

    def _detect_repetition(self, message: DebateMessage, history: list[DebateMessage]) -> bool:
        return detect_repetition(message, history)

    def _detect_contradiction(self, message: DebateMessage, own_history: list[DebateMessage]) -> bool:
        return detect_contradiction(message, own_history)
