"""deep_research tool — primary web search via Gemini with Perplexity fallback."""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from article_writer.shared.constants import CONFIDENCE_LOW
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger
from article_writer.tools.base_tool import ArticleBaseTool

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

_GEMINI_PROMPT = (
    "Search for: {prompt}. Provide a factual, comprehensive answer "
    "with citations from credible sources. Include URLs for all sources."
)


class DeepResearchTool(ArticleBaseTool):
    """Calls Gemini (primary) or Perplexity (fallback) for web research with citations."""

    name: str = "deep_research"
    description: str = (
        "Search the web for factual information on a topic. "
        "Input: a research query as plain text in the 'prompt' field. "
        "Returns: answer with cited sources and confidence level (HIGH/MEDIUM)."
    )
    _PROMPT_TEMPLATE: ClassVar[str] = _GEMINI_PROMPT

    def _run(self, prompt: str) -> str:
        clean = self._sanitize_input(prompt)
        self._log_call(clean)
        gate = ApiGatekeeper()
        result = self._try_gemini(clean, gate) or self._try_perplexity(clean, gate)
        if not result or result.get("confidence") == CONFIDENCE_LOW:
            logger.warning("deep_research: no usable result for query '%s'", clean[:60])
            return ""
        return self._format_result(result)

    def _try_gemini(self, prompt: str, gate: ApiGatekeeper) -> dict | None:
        try:
            from article_writer.mcp.gemini_client import GeminiClient
            return GeminiClient(gate).search(prompt)
        except Exception as exc:
            logger.warning("Gemini search failed: %s — trying fallback", exc)
            return None

    def _try_perplexity(self, prompt: str, gate: ApiGatekeeper) -> dict | None:
        try:
            from article_writer.mcp.perplexity_client import PerplexityClient
            return PerplexityClient(gate).search(prompt)
        except Exception as exc:
            logger.error("Perplexity fallback also failed: %s", exc)
            return None

    def _format_result(self, result: dict) -> str:
        answer = result.get("answer", "")
        citations = result.get("citations", [])
        confidence = result.get("confidence", "MEDIUM")
        cit_lines = "\n".join(
            f"- [{c.get('title', c.get('url', 'Source'))}]({c.get('url', '')})"
            for c in citations
        )
        return (
            f"## Answer\n{answer}\n\n"
            f"## Citations\n{cit_lines or '(no citations returned)'}\n\n"
            f"**Confidence:** {confidence}"
        )
