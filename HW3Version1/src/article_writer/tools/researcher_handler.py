"""researcher_handler tool — session manager for multi-turn research."""
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

_PROMPT_TEMPLATE = (
    "Given research intent: '{prompt}'.\n"
    "Previously searched: {previous_queries}.\n"
    "Suggest exactly 3 new search queries covering angles NOT yet searched.\n"
    "Return JSON only: {{\"new_queries\": [...], \"summary_so_far\": \"...\"}}"
)


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
    _PROMPT_TEMPLATE: ClassVar[str] = _PROMPT_TEMPLATE
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
        llm_prompt = _PROMPT_TEMPLATE.format(
            prompt=clean,
            previous_queries=self._session.previous_queries[:-1] or ["(none yet)"],
        )
        try:
            gate = ApiGatekeeper()
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            def _call() -> anthropic.types.Message:
                return client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=512,
                    messages=[{"role": "user", "content": llm_prompt}],
                )
            response = gate.execute("anthropic", _call)
            raw = response.content[0].text
            parsed = json.loads(raw)
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
