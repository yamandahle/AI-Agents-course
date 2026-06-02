"""Detection helpers for FatherAgent — agreement, repetition, contradiction."""

from __future__ import annotations

from debate.agents.models import DebateMessage

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

_NEGATION_WORDS: tuple[str, ...] = (
    " not ", " never ", "doesn't", "isn't", "aren't", "won't", "can't",
    "no longer", "actually no", "that's wrong", "that is wrong",
)


def detect_agreement(message: DebateMessage) -> bool:
    content_lower = message.content.lower()
    return any(phrase in content_lower for phrase in _AGREEMENT_PHRASES)


def detect_repetition(message: DebateMessage, history: list[DebateMessage]) -> bool:
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


def detect_contradiction(message: DebateMessage, own_history: list[DebateMessage]) -> bool:
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
