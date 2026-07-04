"""FastMCP server for the Thief agent: observe, message, move (no barrier)."""

from fastmcp import FastMCP

from cop_thief.mcp.tools import (
    GameContext,
    GameNotStartedError,
    get_observation_dict,
    make_move_impl,
    send_message_impl,
)

mcp = FastMCP("thief-agent")
_ctx: GameContext | None = None


def set_context(ctx: GameContext) -> None:
    """Inject game context; called by orchestrator before each sub-game."""
    global _ctx
    _ctx = ctx


def clear_context() -> None:
    """Remove game context after sub-game ends."""
    global _ctx
    _ctx = None


def _require_ctx() -> GameContext:
    if _ctx is None:
        raise GameNotStartedError("Game context not set.")
    return _ctx


@mcp.tool()
def get_observation() -> dict:
    """Return the thief's current fog-of-war observation."""
    return get_observation_dict(_require_ctx())


@mcp.tool()
def send_message(message: str) -> dict:
    """Send a natural-language message to the cop."""
    return send_message_impl(_require_ctx(), message)


@mcp.tool()
def make_move(direction: str) -> dict:
    """Move the thief one cell in direction (N/NE/E/SE/S/SW/W/NW)."""
    return make_move_impl(_require_ctx(), direction)
