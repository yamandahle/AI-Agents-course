"""content_filter tool — LLM-based relevance and trustworthiness scorer."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import ClassVar

import anthropic
from dotenv import load_dotenv

from article_writer.shared.constants import CONFIDENCE_LOW
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger
from article_writer.tools.base_tool import ArticleBaseTool

load_dotenv()
logger = get_logger(__name__)

_FILTER_PROMPT = (
    "You are a fact-checker. Rate the content below for relevance to '{topic}' "
    "and trustworthiness (0-100 each).\n"
    "HIGH: both ≥80. MEDIUM: both ≥50 (or one ≥80 and other ≥40). LOW: either <50.\n"
    'Content: "{content}"\n'
    'Return JSON only: {{"keep": true/false, "confidence": "HIGH"|"MEDIUM"|"LOW", "reason": "..."}}'
)


@dataclass
class ContentFilterResult:
    keep: bool
    confidence: str
    reason: str


class ContentFilterTool(ArticleBaseTool):
    """Scores content as HIGH/MEDIUM/LOW confidence. Automatically discards LOW content."""

    name: str = "content_filter"
    description: str = (
        "Evaluates a content chunk for relevance and trustworthiness. "
        "Input: 'content chunk | Topic: article topic' in the 'prompt' field. "
        "Returns: KEEP:HIGH/MEDIUM:reason or DISCARD:LOW:reason."
    )
    _PROMPT_TEMPLATE: ClassVar[str] = _FILTER_PROMPT

    def _run(self, prompt: str) -> str:
        clean = self._sanitize_input(prompt)
        self._log_call(clean)
        parts = clean.split(" | Topic: ", 1)
        content = parts[0].strip()
        topic = parts[1].strip() if len(parts) > 1 else "general"
        result = self._score(content, topic)
        action = "KEEP" if result.keep else "DISCARD"
        return f"{action}:{result.confidence}:{result.reason}"

    def _score(self, content: str, topic: str) -> ContentFilterResult:
        llm_prompt = _FILTER_PROMPT.format(topic=topic, content=content[:2000])
        try:
            gate = ApiGatekeeper()
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            def _call() -> anthropic.types.Message:
                return client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=200,
                    messages=[{"role": "user", "content": llm_prompt}],
                )
            response = gate.execute("anthropic", _call)
            data = json.loads(response.content[0].text)
            confidence = data.get("confidence", CONFIDENCE_LOW)
            keep = data.get("keep", False) and confidence != CONFIDENCE_LOW
            return ContentFilterResult(keep=keep, confidence=confidence, reason=data.get("reason", ""))
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("content_filter JSON parse error: %s — defaulting to DISCARD", exc)
            return ContentFilterResult(keep=False, confidence=CONFIDENCE_LOW, reason="Parse error")
