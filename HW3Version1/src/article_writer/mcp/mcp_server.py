"""MCP server — exposes all 4 research tools over the MCP protocol (stdio transport)."""
from __future__ import annotations

import asyncio
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from article_writer.shared.gatekeeper import ApiGatekeeper

_server = Server("article-writer-research-server")
_gate = ApiGatekeeper()

_TOOLS = [
    types.Tool(
        name="deep_research",
        description="Search the web for factual information. Input: research query. Returns answer with citations.",
        inputSchema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
    ),
    types.Tool(
        name="researcher_handler",
        description="Manage research session state. Tracks visited URLs and suggests new queries.",
        inputSchema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
    ),
    types.Tool(
        name="citation_extractor",
        description="Format a citation from a URL or raw text. Input: URL or text passage.",
        inputSchema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
    ),
    types.Tool(
        name="content_filter",
        description="Score content relevance and trustworthiness. Input: 'content | Topic: topic'.",
        inputSchema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
    ),
]


@_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return _TOOLS


@_server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    prompt = arguments.get("prompt", "")
    from article_writer.tools.deep_research_tool import DeepResearchTool
    from article_writer.tools.researcher_handler import ResearcherHandlerTool
    from article_writer.tools.citation_extractor import CitationExtractorTool
    from article_writer.tools.content_filter import ContentFilterTool

    dispatch = {
        "deep_research": DeepResearchTool,
        "researcher_handler": ResearcherHandlerTool,
        "citation_extractor": CitationExtractorTool,
        "content_filter": ContentFilterTool,
    }
    if name not in dispatch:
        raise ValueError(f"Unknown tool: {name}")
    result = dispatch[name]()._run(prompt)
    return [types.TextContent(type="text", text=result)]


async def main() -> None:
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await _server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="article-writer-research-server",
                server_version="1.00",
                capabilities=_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
