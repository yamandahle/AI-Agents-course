"""
Start the Cop MCP server with a demo game context on port 8001.

Terminal 1:
    uv run python scripts/start_cop_demo.py

Then in Terminal 2:
    uv run python scripts/call_servers.py
"""

import cop_thief.mcp.cop_server as cop_server
from cop_thief.mcp.tools import GameContext
from cop_thief.sdk.game_engine.sub_game import SubGame

SCORING = {"cop_win": 20, "thief_win": 10, "cop_loss": 5, "thief_loss": 5}

sg = SubGame(
    rows=5, cols=5, max_moves=25, max_barriers=5,
    cop_vision_radius=2, thief_vision_radius=2,
    scoring=SCORING,
)
sg.reset(cop_start=(0, 0), thief_start=(4, 4))
store: dict = {"cop": None, "thief": None}

cop_server.set_context(GameContext(
    sub_game=sg,
    agent_id="cop",
    message_store=store,
    max_message_chars=300,
    auth_token="demo-token",
))

print("Cop MCP server starting on http://127.0.0.1:8001")
print("Grid: 5x5 | Cop: (0,0) | Thief: (4,4) | Vision radius: 2")
print("Press Ctrl+C to stop.\n")

cop_server.mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)
