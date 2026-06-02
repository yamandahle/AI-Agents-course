"""_AgentMixin — LLM-call and evidence helpers shared by all debate agents."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any

from debate.agents.models import DebateMessage


class _AgentMixin:
    """Provides LLM calls, JSON extraction, evidence formatting, and prompt building.

    Requires host class to expose: _gatekeeper, _role, _model, _max_tokens,
    _timeout, _skills_path, _word_limit.
    """

    def _build_opening_prompt(self, topic: str) -> str:
        try:
            opening_skill = (Path(self._skills_path) / "open_skill.md").read_text(encoding="utf-8")
        except OSError:
            opening_skill = ""
        return (
            f"YOUR DEBATE ROLE AND POSITION:\n{self.get_skill_prompt()}\n\n"
            f"{opening_skill}\n\n"
            f"DEBATE TOPIC: {topic}\n\n"
            f"Deliver your opening statement. Maximum {self._word_limit} words."
        )

    def _build_prompt(self, opponent_msg: DebateMessage, evidence: str) -> str:
        return (
            f"{self.get_skill_prompt()}\n\n"
            f"OPPONENT'S ARGUMENT (round {opponent_msg.round}):\n{opponent_msg.content}\n\n"
            f"SUPPORTING EVIDENCE FROM WEB SEARCH:\n{evidence}\n\n"
            f"Respond in {self._word_limit} words or fewer. "
            f"Start by directly addressing the opponent's specific claim."
        )

    def _format_evidence(self, results: list[dict[str, str]]) -> str:
        if not results:
            return "No search results available."
        return "\n".join(
            f"- {r['title']}: {r['snippet']} ({r['url']})" for r in results
        )

    def _enforce_word_limit(self, text: str) -> str:
        words = text.split()
        return " ".join(words[: self._word_limit]) if len(words) > self._word_limit else text

    def _extract_concept(self, raw: str) -> str:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return str(parsed.get("new_concept_used", "")).strip().lower()
        except (json.JSONDecodeError, ValueError):
            pass
        return ""

    def _extract_argument(self, raw: str) -> str:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "argument" in parsed:
                return str(parsed["argument"])
        except (json.JSONDecodeError, ValueError):
            pass
        return text

    def _extract_url(self, raw: str) -> str:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                url = str(parsed.get("evidence_url", "")).strip()
                return url if url.startswith("http") else ""
        except (json.JSONDecodeError, ValueError):
            pass
        return ""

    def _call_llm(self, prompt: str) -> str:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            self._gatekeeper.call,
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self._max_tokens,
            agent=self._role,
        )
        try:
            response = future.result(timeout=self._timeout)
            return response.content[0].text
        except FutureTimeoutError:
            raise TimeoutError(
                f"LLM call timed out after {self._timeout}s for role={self._role}"
            ) from None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    # Declared here so type checkers understand the mixin contract
    def get_skill_prompt(self) -> str:  # pragma: no cover
        raise NotImplementedError

    _skills_path: Any
    _word_limit: Any
    _gatekeeper: Any
    _role: Any
    _model: Any
    _max_tokens: Any
    _timeout: Any
