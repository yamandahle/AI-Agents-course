"""Low-level I/O for one turn: calling the LLM and dispatching via MCP tools."""

from cop_thief.sdk.game_engine.board import Action


async def call_llm(gatekeeper, model: str, system_prompt: str, user_prompt: str) -> str:
    """POST the prompt pair to the LLM via ApiGatekeeper; return raw text."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    result = await gatekeeper.call("/api/chat", payload)
    return result["message"]["content"]


async def dispatch_action(client, action: Action, message: str) -> None:
    """Send the message, then apply the move or barrier, via MCP tool calls."""
    await client.send_message(message)
    if action.direction is None:
        await client.place_barrier()
    else:
        await client.make_move(action.direction.name)
