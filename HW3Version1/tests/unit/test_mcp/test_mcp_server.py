"""Tests for mcp/mcp_server.py — MCP protocol handler for research tools."""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch


def test_tools_list_has_four_entries() -> None:
    import article_writer.mcp.mcp_server as ms
    assert len(ms._TOOLS) == 4
    names = {t.name for t in ms._TOOLS}
    assert names == {"deep_research", "researcher_handler", "citation_extractor", "content_filter"}


def test_handle_list_tools_returns_all_tools() -> None:
    import article_writer.mcp.mcp_server as ms
    tools = asyncio.run(ms.handle_list_tools())
    assert len(tools) == 4


def test_handle_call_tool_dispatches_deep_research() -> None:
    import article_writer.mcp.mcp_server as ms
    mock_tool = MagicMock()
    mock_tool.return_value._run.return_value = "research result"
    with patch("article_writer.mcp.mcp_server.DeepResearchTool", mock_tool, create=True):
        with patch("article_writer.tools.deep_research_tool.DeepResearchTool", mock_tool):
            result = asyncio.run(ms.handle_call_tool("deep_research", {"prompt": "AI query"}))
    assert len(result) == 1
    assert result[0].text == "research result"


def test_handle_call_tool_unknown_raises_value_error() -> None:
    import article_writer.mcp.mcp_server as ms
    import pytest
    with pytest.raises(ValueError, match="Unknown tool"):
        asyncio.run(ms.handle_call_tool("nonexistent_tool", {"prompt": "x"}))


def test_handle_call_tool_citation_extractor() -> None:
    import article_writer.mcp.mcp_server as ms
    mock_tool = MagicMock()
    mock_tool.return_value._run.return_value = "[Title](url)"
    with patch("article_writer.tools.citation_extractor.CitationExtractorTool", mock_tool):
        result = asyncio.run(ms.handle_call_tool("citation_extractor", {"prompt": "https://example.com"}))
    assert result[0].text == "[Title](url)"
