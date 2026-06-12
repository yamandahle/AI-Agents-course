"""Gemini API client — primary web search backend for deep_research tool."""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from article_writer.shared.constants import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_MODEL = "gemini-2.5-flash"


class GeminiClient:
    """Wraps Gemini API with gatekeeper-enforced rate limits."""

    def __init__(self, gatekeeper: ApiGatekeeper) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment")
        self._client = genai.Client(api_key=api_key)
        self._gate = gatekeeper

    def search(self, prompt: str) -> dict[str, Any]:
        """Run a grounded web search query. Returns answer, citations, confidence."""
        def _call() -> Any:
            return self._client.models.generate_content(
                model=_MODEL,
                contents=f"Answer this research query with citations from credible sources:\n{prompt}",
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )

        response = self._gate.execute("gemini", _call)
        answer = response.text or ""
        citations = self._extract_citations(response)
        confidence = CONFIDENCE_HIGH if citations else CONFIDENCE_MEDIUM
        meta = response.usage_metadata
        logger.log_token_usage(
            "gemini",
            getattr(meta, "prompt_token_count", 0),
            getattr(meta, "candidates_token_count", 0),
        )
        return {"answer": answer, "citations": citations, "confidence": confidence}

    def _extract_citations(self, response: Any) -> list[dict]:
        citations: list[dict] = []
        try:
            chunks = response.candidates[0].grounding_metadata.grounding_chunks
            for chunk in chunks:
                if hasattr(chunk, "web") and chunk.web:
                    citations.append({"title": chunk.web.title, "url": chunk.web.uri})
        except (AttributeError, IndexError):
            pass
        return citations
