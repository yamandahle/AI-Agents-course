"""Thin async wrapper around FastMCP calls to a single agent's MCP server."""

import os

from fastmcp import Client


class McpClient:
    """Calls one agent's MCP server tools, attaching the Bearer auth token.

    Holds a single persistent connection for the life of the game instead of
    opening/closing one per call -- call `connect()` once before the first tool
    call and `close()` once when the game ends (see main.py's run_game()).
    """

    def __init__(self, base_url: str, auth_token: str | None = None):
        self.base_url = base_url
        self._auth_token = auth_token or os.environ.get("MCP_AUTH_TOKEN", "")
        self._client = Client(base_url)

    def _auth_args(self) -> dict:
        return {"authorization": f"Bearer {self._auth_token}"}

    async def connect(self) -> None:
        """Open the persistent connection. Call once before any tool calls."""
        await self._client.__aenter__()

    async def close(self) -> None:
        """Close the persistent connection. Call once when the game ends."""
        await self._client.__aexit__(None, None, None)

    async def get_observation(self) -> dict:
        """Call get_observation and return the parsed result data."""
        result = await self._client.call_tool("get_observation", self._auth_args())
        return result.data

    async def send_message(self, message: str) -> dict:
        """Send a natural-language message to the opponent."""
        args = {"message": message, **self._auth_args()}
        result = await self._client.call_tool("send_message", args)
        return result.data

    async def make_move(self, direction: str) -> dict:
        """Move one cell in the given direction (N/NE/E/SE/S/SW/W/NW)."""
        args = {"direction": direction, **self._auth_args()}
        result = await self._client.call_tool("make_move", args)
        return result.data

    async def place_barrier(self) -> dict:
        """Place a barrier on the cop's current cell (cop server only)."""
        result = await self._client.call_tool("place_barrier", self._auth_args())
        return result.data


def build_client(
    agent_id: str, config: dict, auth_token: str | None = None
) -> McpClient:
    """Build an McpClient pointed at the correct agent's port from config."""
    port_key = "cop_port" if agent_id == "cop" else "thief_port"
    port = config["mcp"][port_key]
    return McpClient(f"http://127.0.0.1:{port}/mcp", auth_token=auth_token)
