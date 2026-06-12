"""researcher_handler tool — session manager for multi-turn research."""
from __future__ import annotations

import json
import os
from typing import ClassVar

from dotenv import load_dotenv

from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.llm_client import LLMClient, LLMResponse
from article_writer.shared.logger import get_logger
from article_writer.tools.base_tool import ArticleBaseTool

load_dotenv()
logger = get_logger(__name__)

_SYSTEM = "You are a research query planner. Return only valid JSON."
_USER_TEMPLATE = (
    "Given research intent: '{prompt}'.\n"
    "Previously searched: {previous_queries}.\n"
    "Suggest exactly 3 new search queries covering angles NOT yet searched.\n"
    'Return JSON only: {{"new_queries": [...], "summary_so_far": "..."}}'
)

_PROVIDER_TO_SERVICE = {"anthropic": "anthropic", "google": "gemini"}


class _ResearchSession:
    visited_urls: set[str]
    previous_queries: list[str]
    batch_count: int

    def __init__(self) -> None:
        self.visited_urls = set()
        self.previous_queries = []
        self.batch_count = 0


class ResearcherHandlerTool(ArticleBaseTool):
    """Tracks research session state and suggests non-duplicate search queries."""

    name: str = "researcher_handler"
    description: str = (
        "Manages a multi-turn research session. Tracks visited URLs and previous queries "
        "to avoid repetition. Input: current research intent as plain text in 'prompt'. "
        "Returns JSON with suggested new queries and a session summary."
    )
    _USER_TEMPLATE: ClassVar[str] = _USER_TEMPLATE
    _session: _ResearchSession = None  # type: ignore[assignment]

    def model_post_init(self, __context: object) -> None:
        self._session = _ResearchSession()

    def _run(self, prompt: str) -> str:
        if self._session is None:
            self._session = _ResearchSession()
        clean = self._sanitize_input(prompt)
        self._log_call(clean)
        self._session.previous_queries.append(clean)
        self._session.batch_count += 1
        user = _USER_TEMPLATE.format(
            prompt=clean,
            previous_queries=self._session.previous_queries[:-1] or ["(none yet)"],
        )
        try:
            provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
            service = _PROVIDER_TO_SERVICE.get(provider, provider)
            gate = ApiGatekeeper()
            llm = LLMClient()

            def _call() -> LLMResponse:
                return llm.complete(system=_SYSTEM, user=user,
                                    step="researcher_handler", max_tokens=512)

            resp = gate.execute(service, _call)
            parsed = json.loads(self.strip_json_fence(resp.text))
            parsed["batch"] = self._session.batch_count
            return json.dumps(parsed)
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("researcher_handler fallback triggered: %s", exc)
            fallback = [f"{clean} (angle {i})" for i in range(1, 4)]
            return json.dumps({
                "batch": self._session.batch_count,
                "new_queries": fallback,
                "summary_so_far": "Unavailable",
            })

    def reset_session(self) -> None:
        self._session = _ResearchSession()
