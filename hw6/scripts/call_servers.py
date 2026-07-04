"""
Call the running Cop & Thief MCP servers and save results.

Requires servers already running:
    Terminal 1: uv run python scripts/start_cop_demo.py
    Terminal 2: uv run python scripts/start_thief_demo.py   (optional)

Then run this script:
    Terminal 3: uv run python scripts/call_servers.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastmcp import Client

COP_URL      = "http://127.0.0.1:8001/mcp"
THIEF_URL    = "http://127.0.0.1:8002/mcp"
RESULTS_FILE = Path(__file__).parent.parent / "results" / "mcp_demo.json"
AUTH         = {"authorization": "Bearer demo-token"}

log: list = []


def pr(section: str, data) -> None:
    """Print and record a result entry."""
    # list_tools() returns list of Tool objects (have .name but not .text)
    is_tool_list = (
        isinstance(data, list) and data and hasattr(data[0], "name")
        and not hasattr(data[0], "text")
    )
    if is_tool_list:
        parsed = [{"name": t.name, "description": t.description} for t in data]
    # call_tool() returns a CallToolResult with .data (parsed dict)
    elif hasattr(data, "data"):
        parsed = data.data
    else:
        parsed = str(data)

    log.append({"call": section, "result": parsed})
    print(f"\n{'-'*55}")
    print(f"  {section}")
    print(f"{'-'*55}")
    print(json.dumps(parsed, indent=2))


async def demo_cop() -> None:
    print("\n" + "=" * 55)
    print("  COP SERVER  (port 8001)")
    print("=" * 55)
    async with Client(COP_URL) as c:
        pr("cop.list_tools()", await c.list_tools())
        pr("cop.get_observation()",
           await c.call_tool("get_observation", AUTH))
        pr("cop.send_message('I am closing in!')",
           await c.call_tool("send_message", {"message": "I am closing in!", **AUTH}))
        pr("cop.make_move('S')",
           await c.call_tool("make_move", {"direction": "S", **AUTH}))
        pr("cop.place_barrier()",
           await c.call_tool("place_barrier", AUTH))


async def demo_thief() -> None:
    print("\n" + "=" * 55)
    print("  THIEF SERVER  (port 8002)")
    print("=" * 55)
    try:
        async with Client(THIEF_URL) as c:
            pr("thief.list_tools()", await c.list_tools())
            pr("thief.get_observation()",
               await c.call_tool("get_observation", AUTH))
            pr("thief.send_message('You will never catch me!')",
               await c.call_tool("send_message",
                                 {"message": "You will never catch me!", **AUTH}))
            pr("thief.make_move('N')",
               await c.call_tool("make_move", {"direction": "N", **AUTH}))
    except Exception:
        print("  (Thief server not running on port 8002 -- skipped)")
        print("  Start it with: uv run python scripts/start_thief_demo.py")


async def main() -> None:
    await demo_cop()
    await demo_thief()

    RESULTS_FILE.parent.mkdir(exist_ok=True)
    output = {
        "timestamp": datetime.now().isoformat(),
        "demo": "MCP servers -- Cop (8001) & Thief (8002)",
        "calls": log,
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2))
    print(f"\n\nResults saved -> {RESULTS_FILE}")
    print("Done.\n")


if __name__ == "__main__":
    asyncio.run(main())
