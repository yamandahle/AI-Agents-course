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
class DebateResult:
    """Final output of a completed debate session."""

    winner: str
    pro_score: float
    con_score: float
    total_interventions: int
    rounds_completed: int
    transcript: list = field(default_factory=list)
    context_tokens: int = 0


class ArgumentScorer:
    """Score a debate side based on strength, evidence, and persuasion."""

    _WEIGHTS: dict[str, float] = {"strength": 0.40, "evidence": 0.40, "persuasion": 0.20}

    def score(self, history: list[DebateMessage], word_limit: int) -> float:
        if not history:
            return 0.0
        raw = (
            self._score_strength(history, word_limit) * self._WEIGHTS["strength"]
            + self._score_evidence(history) * self._WEIGHTS["evidence"]
            + self._score_persuasion(history) * self._WEIGHTS["persuasion"]
        )
        return min(100.0, max(0.0, raw))

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
