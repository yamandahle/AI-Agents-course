"""Phase 3b — applies evaluator critique to revise the LaTeX draft."""
from __future__ import annotations

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from article_writer.shared.constants import DEFAULT_ENCODING, RESULTS_DIR
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_REVISION_PROMPT = (
    "You are editing a LaTeX article. Apply ALL of the following critique points "
    "to the draft. Do not remove content that was not critiqued. "
    "Do not shrink the article below 15 pages.\n\n"
    "Critique points:\n{critique}\n\n"
    "Current draft:\n{draft}\n\n"
    "Return the complete revised LaTeX source."
)
_REQUIRED_MARKERS = (r"\begin{document}", r"\end{document}")


class Optimizer:
    """Revises the LaTeX draft based on evaluator critique."""

    def __init__(self, iteration: int, config_model: str = "claude-sonnet-4-6") -> None:
        self._iteration = iteration
        self._model = config_model
        self._gate = ApiGatekeeper()

    def optimize(self, draft_path: Path, critique_path: Path) -> Path:
        draft = draft_path.read_text(encoding=DEFAULT_ENCODING)
        critique = critique_path.read_text(encoding=DEFAULT_ENCODING)
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        def _call() -> anthropic.types.Message:
            return client.messages.create(
                model=self._model,
                max_tokens=8192,
                messages=[{
                    "role": "user",
                    "content": _REVISION_PROMPT.format(critique=critique, draft=draft[:6000]),
                }],
            )

        response = self._gate.execute("anthropic", _call)
        revised = response.content[0].text
        self._validate(revised)
        new_path = self._save(revised)
        diff = len(revised.splitlines()) - len(draft.splitlines())
        logger.info("Optimizer iteration %d: diff %+d lines", self._iteration, diff)
        return new_path

    def _validate(self, source: str) -> None:
        for marker in _REQUIRED_MARKERS:
            if marker not in source:
                raise ValueError(f"Optimized draft missing required LaTeX marker: {marker}")

    def _save(self, source: str) -> Path:
        out = Path(RESULTS_DIR) / f"draft_v{self._iteration + 1}.tex"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(source, encoding=DEFAULT_ENCODING)
        logger.info("Optimized draft saved: %s", out)
        return out
