"""
Demo: prove both MCP servers work by calling their tools with a real game context.
Run: uv run python demo_mcp.py
"""

import asyncio
import json

from fastmcp import Client

import cop_thief.mcp.cop_server as cop_server
import cop_thief.mcp.thief_server as thief_server
from cop_thief.mcp.tools import GameContext
from cop_thief.sdk.game_engine.sub_game import SubGame

SCORING = {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5}
AUTH = {"authorization": "Bearer demo-token"}


def show(label: str, result) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print('='*50)
    if isinstance(result, list):
        for tool in result:
            print(f"{tool.name}: {tool.description}")
    else:
        print(json.dumps(result.data, indent=2))


async def main() -> None:
    # ── Setup ──────────────────────────────────────────────────────────────────
    sg = SubGame(
        rows=5, cols=5, max_moves=25, max_barriers=5,
        cop_vision_radius=2, thief_vision_radius=2,
        scoring=SCORING,
    )
    sg.reset(cop_start=(0, 0), thief_start=(4, 4))
    store: dict = {"cop": None, "thief": None}

    thief_server.set_context(GameContext(sg, "thief", store, 300, "demo-token"))
    cop_server.set_context(GameContext(sg, "cop",   store, 300, "demo-token"))

    print("\nStarting positions: cop=(0,0)  thief=(4,4)  vision_radius=2")

    # ── Thief turn ─────────────────────────────────────────────────────────────
    async with Client(thief_server.mcp) as tc:
        show("THIEF list_tools()", await tc.list_tools())

        show("THIEF get_observation()", await tc.call_tool("get_observation", AUTH))

        show("THIEF send_message('You will never catch me!')",
             await tc.call_tool("send_message",
                                {"message": "You will never catch me!", **AUTH}))

        show("THIEF make_move('N') -> moves to (3,4)",
             await tc.call_tool("make_move", {"direction": "N", **AUTH}))

    # ── Cop turn ───────────────────────────────────────────────────────────────
    async with Client(cop_server.mcp) as cc:
        show("COP list_tools()", await cc.list_tools())

        show("COP get_observation()  (last_message = thief's taunt)",
             await cc.call_tool("get_observation", AUTH))

        show("COP make_move('S') -> moves to (1,0)",
             await cc.call_tool("make_move", {"direction": "S", **AUTH}))

        show("COP place_barrier()  (barrier at (1,0))",
             await cc.call_tool("place_barrier", AUTH))

    print("\nAll tools called successfully.\n")


if __name__ == "__main__":
    asyncio.run(main())
