"""Shared MCP tool functions: observation, messaging, movement, barrier."""

from dataclasses import dataclass
from typing import Any

from cop_thief.sdk.game_engine.board import Action, Direction, InvalidMoveError


class AuthError(Exception):
    """Raised when the Bearer token is missing or invalid."""


class MessageTooLongError(Exception):
    """Raised when a message exceeds the configured character limit."""


class GameNotStartedError(Exception):
    """Raised when a tool is called before the game context is injected."""


@dataclass
class GameContext:
    """Runtime state injected into both MCP servers by the orchestrator."""

    sub_game: Any
    agent_id: str
    message_store: dict       # {"cop": str|None, "thief": str|None}
    max_message_chars: int
    auth_token: str           # expected token (without "Bearer " prefix)


def check_auth(authorization: str, expected_token: str) -> None:
    """Raise AuthError if authorization header value does not match token."""
    token = authorization.removeprefix("Bearer ").strip()
    if not token or token != expected_token:
        raise AuthError("Invalid or missing token.")


def get_observation_dict(ctx: GameContext) -> dict:
    """Return agent's fog-of-war observation as a JSON-serialisable dict."""
    last_msg = ctx.message_store.get(ctx.agent_id)
    obs = ctx.sub_game.get_observation(ctx.agent_id, last_msg)
    return {
        "own_position": list(obs.own_position),
        "barriers": [list(b) for b in obs.barriers],
        "move_counter": obs.move_counter,
        "opponent_pos": list(obs.opponent_pos) if obs.opponent_pos else None,
        "last_message": obs.last_message,
    }


def send_message_impl(ctx: GameContext, message: str) -> dict:
    """Store message in message_store for delivery to opponent's next observation."""
    if len(message) > ctx.max_message_chars:
        raise MessageTooLongError(
            f"Message exceeds {ctx.max_message_chars} chars."
        )
    opponent = "thief" if ctx.agent_id == "cop" else "cop"
    ctx.message_store[opponent] = message
    return {"status": "ok"}


def make_move_impl(ctx: GameContext, direction: str) -> dict:
    """Move the agent one cell in the given direction."""
    try:
        dir_enum = Direction[direction.upper()]
    except KeyError:
        raise InvalidMoveError(f"Unknown direction: {direction!r}")
    action = Action(dir_enum)
    if ctx.agent_id == "thief":
        ctx.sub_game.apply_thief_action(action)
    else:
        ctx.sub_game.apply_cop_action(action)
    pos = ctx.sub_game.board.get_agent_pos(ctx.agent_id)
    return {"status": "ok", "new_position": list(pos)}


def place_barrier_impl(ctx: GameContext) -> dict:
    """Place a barrier at the cop's current cell instead of moving."""
    pos = ctx.sub_game.board.get_agent_pos("cop")
    ctx.sub_game.apply_cop_action(Action(direction=None))
    return {
        "status": "ok",
        "barrier_placed_at": list(pos),
        "barriers_remaining": ctx.sub_game.board.barriers_remaining,
    }
