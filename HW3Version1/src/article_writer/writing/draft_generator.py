"""Phase 2 — generates the initial LaTeX draft from unified writer context."""
from __future__ import annotations

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from article_writer.shared.config import AppConfig, load_config
from article_writer.shared.constants import RESULTS_DIR
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert LaTeX academic article writer. Generate a complete, "
    "compilable LaTeX source file for an article of at least 15 pages. "
    "The output MUST start with \\documentclass and include \\begin{document} "
    "and \\end{document}. Include \\maketitle and \\tableofcontents. "
    "Use lualatex-compatible packages only."
)

_REQUIRED_MARKERS = (r"\begin{document}", r"\end{document}", r"\tableofcontents", r"\maketitle")


class DraftGenerator:
    """Generates the initial LaTeX draft from combined writer context."""

    def __init__(self, context: str, config: AppConfig | None = None) -> None:
        self._context = context
        self._config = config or load_config()
        self._gate = ApiGatekeeper()

    def generate(self) -> Path:
        """Call LLM to generate draft, validate, save to results/draft_v1.tex."""
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        user_msg = (
            f"Write a complete LaTeX article (≥{self._config.writing.target_pages} pages) "
            f"based on the following context:\n\n{self._context}"
        )

        def _call() -> anthropic.types.Message:
            return client.messages.create(
                model=self._config.llm.model,
                max_tokens=8192,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )

        response = self._gate.execute("anthropic", _call)
        latex_source = response.content[0].text
        logger.log_token_usage(
            "anthropic",
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        self._validate(latex_source)
        return self._save(latex_source, "draft_v1.tex")

    def _validate(self, source: str) -> None:
        for marker in _REQUIRED_MARKERS:
            if marker not in source:
                raise ValueError(f"Generated LaTeX missing required marker: {marker}")

    def _save(self, source: str, filename: str) -> Path:
        out_dir = Path(RESULTS_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / filename
        path.write_text(source, encoding="utf-8")
        logger.info("Draft saved: %s (%d chars)", path, len(source))
        return path
