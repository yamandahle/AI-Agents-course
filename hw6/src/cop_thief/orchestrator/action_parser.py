"""Parse the LLM's raw text response into a message and an Action."""

import re

from cop_thief.sdk.game_engine.board import Action, Direction

MESSAGE_RE = re.compile(r"MESSAGE:\s*(.+?)\s*(?=ACTION:|\n|$)", re.IGNORECASE)
# `[*_`]*` tolerates Markdown emphasis (e.g. "**Action:** NW") sitting directly
# against the colon with no whitespace -- \w+ still stops at the next non-word
# character, so a trailing "**" after the value is never captured either.
ACTION_RE = re.compile(r"ACTION:\s*[*_`]*\s*(\w+)", re.IGNORECASE)


def parse_response(llm_response: str) -> tuple[str, Action | None]:
    """Extract (message, Action) from an LLM response.

    Returns action=None if no valid ACTION token is found — callers should
    treat that as a parse failure and retry, per the orchestrator's retry policy.
    """
    message_match = MESSAGE_RE.search(llm_response)
    message = message_match.group(1).strip() if message_match else ""

    action_match = ACTION_RE.search(llm_response)
    action = None
    if action_match:
        token = action_match.group(1).upper()
        if token == "BARRIER":
            action = Action(direction=None)
        elif token in Direction.__members__:
            action = Action(direction=Direction[token])
    return message, action
