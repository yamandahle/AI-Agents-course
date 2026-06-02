"""FatherAgent — neutral moderator that routes, detects violations, and scores the debate."""

from __future__ import annotations

import json
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

_NEGATION_WORDS: tuple[str, ...] = (
    " not ", " never ", "doesn't", "isn't", "aren't", "won't", "can't",
    "no longer", "actually no", "that's wrong", "that is wrong",
)


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
        compactions = 0
        context_tokens = 0
        pro_concepts: list[str] = []
        con_concepts: list[str] = []
        pro_contradictions = 0
        con_contradictions = 0
        pro_urls_seen: set[str] = set()
        con_urls_seen: set[str] = set()
        pro_rounds_won = 0
        con_rounds_won = 0
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
            if pro_msg.concept and pro_msg.concept not in pro_concepts:
                pro_concepts.append(pro_msg.concept)
            if self._detect_contradiction(pro_msg, pro_history):
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
            con_msg, n = self._check_and_intervene(
                con_msg, con_agent, "con", pro_msg, con_history, on_event,
            )
            interventions += n
            if con_msg.concept and con_msg.concept not in con_concepts:
                con_concepts.append(con_msg.concept)
            if self._detect_contradiction(con_msg, con_history):
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
            self._fire(on_event, "round_result", {
                "round": rnd, "winner": rnd_winner, "reason": rnd_reason,
                "pro_rounds_won": pro_rounds_won, "con_rounds_won": con_rounds_won,
            })

            round_tokens = round(
                (pro_msg.word_count + con_msg.word_count) * self._token_multiplier
            )
            context_tokens += round_tokens
            self._fire(on_event, "context_update", {"round": rnd, "new_tokens": round_tokens, "total": context_tokens})

            if self._logger is not None:
                self._logger.info("father", "context_update", {"round": rnd, "new_tokens": round_tokens, "total": context_tokens})

            if rnd % self._summarize_after == 0:
                compactions += 1
                summary = self._summarize_history(pro_history + con_history)
                if self._logger is not None:
                    self._logger.info("father", "context_compact", {
                        "rounds_summarized": f"1-{rnd}", "tokens_saved": context_tokens // 2, "summary": summary,
                    })
                self._fire(on_event, "context_compact", {"saved": context_tokens // 2, "summary": summary})

            current_msg = con_msg

        result = self._produce_verdict(
            pro_history, con_history, transcript, interventions, context_tokens,
            pro_concepts=pro_concepts, con_concepts=con_concepts,
            pro_contradictions=pro_contradictions, con_contradictions=con_contradictions,
            compactions=compactions,
            pro_rounds_won=pro_rounds_won,
            con_rounds_won=con_rounds_won,
        )
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
        pro_concepts: list[str] | None = None,
        con_concepts: list[str] | None = None,
        pro_contradictions: int = 0,
        con_contradictions: int = 0,
        compactions: int = 0,
        pro_rounds_won: int = 0,
        con_rounds_won: int = 0,
    ) -> DebateResult:
        # Breakdown kept for display transparency
        pro_bd = self._scorer.score_detailed(
            pro_history, self._word_limit,
            len(pro_concepts or []), pro_contradictions,
        )
        con_bd = self._scorer.score_detailed(
            con_history, self._word_limit,
            len(con_concepts or []), con_contradictions,
        )

        # Primary score: round tally (60% weight)
        total_rounds = pro_rounds_won + con_rounds_won
        round_pro_pct = (
            50.0 + (pro_rounds_won - con_rounds_won) / total_rounds * 30.0
            if total_rounds > 0 else 50.0
        )

        # Secondary score: LLM self-evaluation (40% weight)
        llm_pro_pct, verdict_reasoning = self._llm_evaluate(
            pro_history, con_history, pro_rounds_won, con_rounds_won,
        )

        if llm_pro_pct is not None:
            pro_pct = round(0.6 * round_pro_pct + 0.4 * llm_pro_pct, 1)
        else:
            pro_pct = round(round_pro_pct, 1)
        con_pct = round(100.0 - pro_pct, 1)

        # Enforce 2-point minimum gap — break in favour of round-tally leader
        if abs(pro_pct - con_pct) < 2.0:
            if pro_rounds_won >= con_rounds_won:
                pro_pct = min(100.0, pro_pct + 1.0)
                con_pct = max(0.0, con_pct - 1.0)
            else:
                con_pct = min(100.0, con_pct + 1.0)
                pro_pct = max(0.0, pro_pct - 1.0)

        winner = "pro" if pro_pct >= con_pct else "con"
        return DebateResult(
            winner=winner, pro_score=pro_pct, con_score=con_pct,
            total_interventions=interventions, rounds_completed=len(pro_history),
            transcript=transcript, context_tokens=context_tokens,
            pro_breakdown=pro_bd, con_breakdown=con_bd,
            total_compactions=compactions,
            verdict_reasoning=verdict_reasoning,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _coach(
        self,
        msg: DebateMessage,
        agent_name: str,
        seen_urls: set[str],
        on_event: _OnEvent,
    ) -> None:
        """Fire coaching events if the argument trips a quality rule."""
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

    def _score_round(self, pro_msg: DebateMessage, con_msg: DebateMessage) -> tuple[str, str]:
        """Determine which agent won this single round based on evidence + depth."""
        pro_ev = self._scorer._score_evidence([pro_msg])
        con_ev = self._scorer._score_evidence([con_msg])
        pro_st = self._scorer._score_strength([pro_msg], self._word_limit)
        con_st = self._scorer._score_strength([con_msg], self._word_limit)
        pro_total = pro_ev * 0.6 + pro_st * 0.4
        con_total = con_ev * 0.6 + con_st * 0.4
        if pro_total > con_total + 2:
            return "pro", "stronger evidence and depth"
        if con_total > pro_total + 2:
            return "con", "stronger evidence and depth"
        if pro_msg.word_count > con_msg.word_count:
            return "pro", "more developed argument"
        if con_msg.word_count > pro_msg.word_count:
            return "con", "more developed argument"
        return "pro", "closely matched — PRO takes the edge"

    def _llm_evaluate(
        self,
        pro_history: list[DebateMessage],
        con_history: list[DebateMessage],
        pro_rounds_won: int,
        con_rounds_won: int,
    ) -> tuple[float | None, str]:
        """Ask the LLM 5 structured questions about the debate. Returns (pro_pct or None, reasoning)."""
        lines = []
        for p, c in zip(pro_history, con_history, strict=False):
            lines.append(f"Round {p.round} PRO: {p.content}")
            lines.append(f"Round {c.round} CON: {c.content}")
        transcript_text = "\n".join(lines)
        prompt = (
            f"{self.get_skill_prompt()}\n\n"
            f"=== FINAL DEBATE EVALUATION ===\n"
            f"Round tally: PRO won {pro_rounds_won}, CON won {con_rounds_won}.\n\n"
            f"FULL TRANSCRIPT:\n{transcript_text}\n\n"
            f"As the neutral judge, score the OVERALL debate on each dimension.\n"
            f"Use 0-10 (0 = CON clearly better, 5 = exactly equal, 10 = PRO clearly better).\n\n"
            f"Q1 Novelty: Which side introduced more original, diverse concepts across all rounds?\n"
            f"Q2 Evidence: Whose evidence was more specific, credible, and hard to dismiss?\n"
            f"Q3 Rebuttal: Who more directly and effectively dismantled the opponent's specific claims?\n"
            f"Q4 Logic: Whose reasoning chain was clearer and harder to attack?\n"
            f"Q5 Persuasion: Who would convince a neutral, informed observer?\n\n"
            f"Respond ONLY with this JSON — no text before or after:\n"
            f'{{"q1_novelty":<0-10>,"q2_evidence":<0-10>,"q3_rebuttal":<0-10>,'
            f'"q4_logic":<0-10>,"q5_persuasion":<0-10>,'
            f'"reasoning":"<2 sentences on who won overall and the single most decisive reason>"}}'
        )
        try:
            raw = self._call_llm(prompt)
            text = str(raw).strip()
            if text.startswith("```"):
                inner = text.splitlines()
                text = "\n".join(inner[1:-1] if inner[-1].strip() == "```" else inner[1:]).strip()
            parsed = json.loads(text)
            scores = [
                float(parsed["q1_novelty"]),
                float(parsed["q2_evidence"]),
                float(parsed["q3_rebuttal"]),
                float(parsed["q4_logic"]),
                float(parsed["q5_persuasion"]),
            ]
            avg = sum(scores) / len(scores)   # 0-10 scale for PRO
            return avg / 10.0 * 100.0, str(parsed.get("reasoning", ""))
        except Exception:  # noqa: BLE001
            return None, ""

    def _detect_contradiction(
        self, message: DebateMessage, own_history: list[DebateMessage],
    ) -> bool:
        """Return True if message negates a concept the same agent previously argued."""
        content_lower = " " + message.content.lower() + " "
        own_concepts = [m.concept.lower() for m in own_history if m.concept]
        if not own_concepts:
            return False
        for concept in own_concepts:
            if concept and concept in content_lower:
                pos = content_lower.find(concept)
                window = content_lower[max(0, pos - 40) : pos + len(concept) + 40]
                if any(neg in window for neg in _NEGATION_WORDS):
                    return True
        return False

    def _summarize_history(self, history: list[DebateMessage]) -> str:
        """Call LLM with the summarize skill to compact the debate transcript."""
        skill_path = Path(self._skills_path) / "summarize_skill.md"
        try:
            skill = skill_path.read_text(encoding="utf-8")
        except OSError:
            return "(summary unavailable)"
        transcript_text = "\n".join(
            f"Round {m.round} [{m.sender.upper()}]: {m.content}" for m in history
        )
        prompt = f"{skill}\n\nDEBATE HISTORY TO SUMMARIZE:\n{transcript_text}"
        try:
            return self._call_llm(prompt)
        except Exception:  # noqa: BLE001
            return "(summary unavailable)"

    def _fire(self, on_event: _OnEvent, event: str, data: dict[str, Any]) -> None:
        if on_event is not None:
            on_event(event, data)
