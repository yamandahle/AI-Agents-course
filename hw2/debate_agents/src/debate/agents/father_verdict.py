"""Standalone scoring functions for FatherAgent verdict production."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING

from debate.agents.father_scoring import ArgumentScorer, DebateResult

if TYPE_CHECKING:
    from debate.agents.models import DebateMessage


def score_round(
    scorer: ArgumentScorer,
    word_limit: int,
    pro_msg: DebateMessage,
    con_msg: DebateMessage,
) -> tuple[str, str]:
    pro_ev = scorer._score_evidence([pro_msg])  # noqa: SLF001
    con_ev = scorer._score_evidence([con_msg])  # noqa: SLF001
    pro_st = scorer._score_strength([pro_msg], word_limit)  # noqa: SLF001
    con_st = scorer._score_strength([con_msg], word_limit)  # noqa: SLF001
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


def llm_evaluate(
    call_llm_fn: Callable[[str], str],
    get_skill_fn: Callable[[], str],
    pro_history: list[DebateMessage],
    con_history: list[DebateMessage],
    pro_rounds_won: int,
    con_rounds_won: int,
) -> tuple[float | None, str]:
    lines: list[str] = []
    for p, c in zip(pro_history, con_history, strict=False):
        lines.append(f"Round {p.round} PRO: {p.content}")
        lines.append(f"Round {c.round} CON: {c.content}")
    transcript_text = "\n".join(lines)
    prompt = (
        f"{get_skill_fn()}\n\n"
        f"=== FINAL DEBATE EVALUATION ===\n"
        f"Round tally: PRO won {pro_rounds_won}, CON won {con_rounds_won}.\n\n"
        f"FULL TRANSCRIPT:\n{transcript_text}\n\n"
        f"Score each question 0-10 (0=CON dominated, 5=equal, 10=PRO dominated):\n"
        f"Q1 Novelty: Which side introduced more original concepts?\n"
        f"Q2 Evidence: Whose evidence was more specific and credible?\n"
        f"Q3 Rebuttal: Who dismantled the opponent's claims more effectively?\n"
        f"Q4 Logic: Whose reasoning was clearer and harder to attack?\n"
        f"Q5 Persuasion: Who would convince a neutral observer?\n\n"
        f"Respond ONLY with JSON:\n"
        f'{{"q1_novelty":<0-10>,"q2_evidence":<0-10>,"q3_rebuttal":<0-10>,'
        f'"q4_logic":<0-10>,"q5_persuasion":<0-10>,'
        f'"reasoning":"<2 sentences on who won and the decisive reason>"}}'
    )
    try:
        raw = call_llm_fn(prompt)
        text = str(raw).strip()
        if text.startswith("```"):
            inner = text.splitlines()
            text = "\n".join(inner[1:-1] if inner[-1].strip() == "```" else inner[1:]).strip()
        parsed = json.loads(text)
        scores = [float(parsed[k]) for k in ("q1_novelty", "q2_evidence", "q3_rebuttal", "q4_logic", "q5_persuasion")]
        return sum(scores) / len(scores) / 10.0 * 100.0, str(parsed.get("reasoning", ""))
    except Exception:  # noqa: BLE001
        return None, ""


def produce_verdict(
    scorer: ArgumentScorer,
    word_limit: int,
    llm_evaluate_fn: Callable,
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
    pro_bd = scorer.score_detailed(pro_history, word_limit, len(pro_concepts or []), pro_contradictions)
    con_bd = scorer.score_detailed(con_history, word_limit, len(con_concepts or []), con_contradictions)

    total_rounds = pro_rounds_won + con_rounds_won
    round_pro_pct = (
        50.0 + (pro_rounds_won - con_rounds_won) / total_rounds * 30.0
        if total_rounds > 0 else 50.0
    )
    llm_pro_pct, verdict_reasoning = llm_evaluate_fn(pro_history, con_history, pro_rounds_won, con_rounds_won)
    pro_pct = round(0.6 * round_pro_pct + 0.4 * llm_pro_pct, 1) if llm_pro_pct is not None else round(round_pro_pct, 1)
    con_pct = round(100.0 - pro_pct, 1)

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
        total_compactions=compactions, verdict_reasoning=verdict_reasoning,
    )
