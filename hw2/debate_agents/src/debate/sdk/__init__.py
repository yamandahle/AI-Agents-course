"""Public SDK surface — all external consumers import from here."""

from debate.sdk.sdk import (
    DebateSDK,
    DebateSession,
    SessionNotFoundError,
    execute_debate,
    get_cost_report,
    get_status,
    get_transcript,
    start_debate,
)

__all__ = [
    "DebateSDK",
    "DebateSession",
    "SessionNotFoundError",
    "execute_debate",
    "get_cost_report",
    "get_status",
    "get_transcript",
    "start_debate",
]
