"""citation_extractor tool — formats citations from URLs or raw text passages."""
from __future__ import annotations

import json
import os
from typing import ClassVar

import anthropic
from dotenv import load_dotenv

from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger
from article_writer.tools.base_tool import ArticleBaseTool

load_dotenv()
logger = get_logger(__name__)

_URL_PROMPT = (
    "Extract citation metadata from this URL: {prompt}\n"
    'Return JSON only: {{"title": "...", "author": "...", "date": "YYYY-MM-DD", "url": "{prompt}"}}\n'
    'Use "Unknown" for any missing field.'
)
_TEXT_PROMPT = (
    'Extract citation information from this text passage: "{prompt}"\n'
    'Return JSON only: {{"title": "...", "author": "...", "date": "YYYY-MM-DD", "publication": "..."}}\n'
    'Use "Unknown" for any missing field.'
)


class CitationExtractorTool(ArticleBaseTool):
    """Extracts and formats citations from URLs or text into markdown link format."""

    name: str = "citation_extractor"
    description: str = (
        "Formats a citation from a URL or raw text passage. "
        "Input: a URL string OR a text passage in the 'prompt' field. "
        "Returns: formatted markdown citation [Title](url) with author and date."
    )
    _URL_PROMPT_TEMPLATE: ClassVar[str] = _URL_PROMPT
    _TEXT_PROMPT_TEMPLATE: ClassVar[str] = _TEXT_PROMPT

    def _run(self, prompt: str) -> str:
        clean = self._sanitize_input(prompt)
        self._log_call(clean)
        is_url = clean.startswith("http://") or clean.startswith("https://")
        llm_prompt = (_URL_PROMPT if is_url else _TEXT_PROMPT).format(prompt=clean)
        try:
            gate = ApiGatekeeper()
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            def _call() -> anthropic.types.Message:
                return client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=256,
                    messages=[{"role": "user", "content": llm_prompt}],
                )
            response = gate.execute("anthropic", _call)
            data = json.loads(response.content[0].text)
            title = data.get("title", "Unknown Source")
            url = data.get("url", clean if is_url else "")
            author = data.get("author", "Unknown")
            date = data.get("date", "n.d.")
            return f"[{title}]({url}) — {author}, {date}"
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("citation_extractor fallback for '%s': %s", clean[:40], exc)
            return f"{clean} (source unverified)"
