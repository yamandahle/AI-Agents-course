"""Perplexity API client — fallback web search backend via OpenAI-compatible API."""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from article_writer.shared.constants import CONFIDENCE_MEDIUM
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_BASE_URL = "https://api.perplexity.ai"
_MODEL = "sonar-pro"


class PerplexityClient:
    """Wraps Perplexity API (OpenAI-compatible) with gatekeeper-enforced rate limits."""

    def __init__(self, gatekeeper: ApiGatekeeper) -> None:
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY is not set in environment")
        self._client = OpenAI(api_key=api_key, base_url=_BASE_URL)
        self._gate = gatekeeper

    def search(self, prompt: str) -> dict[str, Any]:
        """Run a search query via Perplexity. Returns answer, citations, confidence."""
        def _call() -> Any:
            return self._client.chat.completions.create(
                model=_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )

        response = self._gate.execute("perplexity", _call)
        answer = response.choices[0].message.content or ""
        citations = self._extract_citations(response)
        logger.log_token_usage(
            "perplexity",
            response.usage.prompt_tokens if response.usage else 0,
            response.usage.completion_tokens if response.usage else 0,
        )
        return {"answer": answer, "citations": citations, "confidence": CONFIDENCE_MEDIUM}

    def _extract_citations(self, response: Any) -> list[dict]:
        citations: list[dict] = []
        try:
            for citation in getattr(response, "citations", []):
                if isinstance(citation, str):
                    citations.append({"title": citation, "url": citation})
                elif isinstance(citation, dict):
                    citations.append(citation)
        except (AttributeError, TypeError):
            pass
        return citations
