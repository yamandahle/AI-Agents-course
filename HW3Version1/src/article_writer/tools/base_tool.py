"""Base tool mixin — shared sanitization, logging, and formatting for all article-writer tools."""
from __future__ import annotations

import re

from crewai.tools import BaseTool

from article_writer.shared.constants import MAX_SANITIZE_CHARS
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)


class ArticleBaseTool(BaseTool):
    """Mixin providing sanitization and logging for all project tools."""

    def _sanitize_input(self, text: str) -> str:
        """Strip HTML/script tags and truncate to MAX_SANITIZE_CHARS."""
        cleaned = _SCRIPT_RE.sub("", text)
        cleaned = _HTML_TAG_RE.sub("", cleaned)
        return cleaned[:MAX_SANITIZE_CHARS]

    def _log_call(self, sanitized_input: str) -> None:
        logger.info("[TOOL] %s called — input_len=%d", self.name, len(sanitized_input))

    def _format_markdown_output(self, header: str, body: str) -> str:
        """Ensure output starts with a markdown ## header."""
        return f"## {header}\n\n{body}"
