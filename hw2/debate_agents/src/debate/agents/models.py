"""DebateMessage — shared message schema for all debate agents."""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DebateMessage:
    """Structured message exchanged between debate agents."""

    type: str
    round: int
    sender: str
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )
    word_count: int = 0
    concept: str = ""
    evidence_url: str = ""

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DebateMessage:
        return cls(
            type=data["type"],
            round=data["round"],
            sender=data["sender"],
            content=data["content"],
            timestamp=data.get("timestamp", datetime.now(tz=timezone.utc).isoformat()),
            word_count=data.get("word_count", 0),
            evidence_url=data.get("evidence_url", ""),
        )
