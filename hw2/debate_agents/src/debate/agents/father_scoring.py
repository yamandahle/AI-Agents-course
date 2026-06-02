"""Scoring primitives for FatherAgent: DebateResult dataclass and ArgumentScorer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from debate.agents.base_agent import DebateMessage

_EVIDENCE_MARKERS: tuple[str, ...] = (
    "%", "study", "research", "http", "data", "found", "showed", "according", "survey",
)


@dataclass
class ScoreBreakdown:
    """Per-agent scoring detail produced after a completed debate."""

    strength: float
    evidence: float
    persuasion: float
    concept_bonus: float
    contradiction_penalty: float
    total: float
    concepts_introduced: int
    contradictions_found: int


@dataclass
class DebateResult:
    """Final output of a completed debate session."""

    winner: str
    pro_score: float
    con_score: float
    total_interventions: int
    rounds_completed: int
    transcript: list = field(default_factory=list)
    context_tokens: int = 0
    pro_breakdown: ScoreBreakdown | None = None
    con_breakdown: ScoreBreakdown | None = None
    total_compactions: int = 0


class ArgumentScorer:
    """Score a debate side based on strength, evidence, persuasion, concepts, and contradictions."""

    _WEIGHTS: dict[str, float] = {"strength": 0.40, "evidence": 0.40, "persuasion": 0.20}
    _CONCEPT_BONUS_PER: float = 2.0    # points awarded per unique new concept
    _CONTRADICTION_PEN: float = 2.0    # points deducted per self-contradiction

    def score(self, history: list[DebateMessage], word_limit: int) -> float:
        """Return total score as a single float (backward-compatible)."""
        return self.score_detailed(history, word_limit, 0, 0).total

    def score_detailed(
        self,
        history: list[DebateMessage],
        word_limit: int,
        concepts_count: int,
        contradictions_count: int,
    ) -> ScoreBreakdown:
        """Return a full ScoreBreakdown including bonus and penalty adjustments."""
        if not history:
            return ScoreBreakdown(
                strength=0.0, evidence=0.0, persuasion=0.0,
                concept_bonus=0.0, contradiction_penalty=0.0, total=0.0,
                concepts_introduced=0, contradictions_found=0,
            )
        strength = self._score_strength(history, word_limit)
        evidence = self._score_evidence(history)
        persuasion = self._score_persuasion(history)
        base = (
            strength * self._WEIGHTS["strength"]
            + evidence * self._WEIGHTS["evidence"]
            + persuasion * self._WEIGHTS["persuasion"]
        )
        bonus = concepts_count * self._CONCEPT_BONUS_PER
        penalty = contradictions_count * self._CONTRADICTION_PEN
        total = min(100.0, max(0.0, base + bonus - penalty))
        return ScoreBreakdown(
            strength=round(strength, 1),
            evidence=round(evidence, 1),
            persuasion=round(persuasion, 1),
            concept_bonus=round(bonus, 1),
            contradiction_penalty=round(penalty, 1),
            total=round(total, 1),
            concepts_introduced=concepts_count,
            contradictions_found=contradictions_count,
        )

    def _score_strength(self, history: list[DebateMessage], word_limit: int) -> float:
        avg_words = sum(m.word_count for m in history) / len(history)
        return min(100.0, avg_words / word_limit * 100)

    def _score_evidence(self, history: list[DebateMessage]) -> float:
        count = sum(
            1 for m in history
            if any(marker in m.content.lower() for marker in _EVIDENCE_MARKERS)
        )
        return count / len(history) * 100

    def _score_persuasion(self, history: list[DebateMessage]) -> float:
        all_words: list[str] = []
        for m in history:
            all_words.extend(m.content.lower().split())
        if not all_words:
            return 0.0
        return len(set(all_words)) / len(all_words) * 100
