"""Phase 2 — generates the initial LaTeX draft from unified writer context."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from article_writer.shared.config import AppConfig, load_config
from article_writer.shared.constants import RESULTS_DIR
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.llm_client import LLMClient
from article_writer.shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_PROVIDER_TO_SERVICE = {"anthropic": "anthropic", "google": "gemini"}


def _strip_code_fence(text: str) -> str:
    """Strip markdown code fences (```latex or ```) from LLM output."""
    import re
    text = text.strip()
    m = re.search(r"```(?:latex|tex)?\s*([\s\S]+?)\s*```\s*$", text)
    return m.group(1).strip() if m else text

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
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        service = _PROVIDER_TO_SERVICE.get(provider, provider)
        llm = LLMClient()
        user_msg = (
            f"Write a complete LaTeX article (≥{self._config.writing.target_pages} pages) "
            f"based on the following context:\n\n{self._context}"
        )

        def _call():
            return llm.complete(
                system=_SYSTEM_PROMPT,
                user=user_msg,
                step="draft_generation",
                max_tokens=32768,
            )

        response = self._gate.execute(service, _call)
        latex_source = _strip_code_fence(response.text)
        logger.log_token_usage(service, response.input_tokens, response.output_tokens)
        latex_source = self._validate(latex_source)
        return self._save(latex_source, "draft_v1.tex")

    def _validate(self, source: str) -> str:
        """Warn on missing markers; inject \maketitle if absent (non-fatal)."""
        for marker in _REQUIRED_MARKERS[:2]:  # \begin{document}, \end{document} are hard requirements
            if marker not in source:
                raise ValueError(f"Generated LaTeX missing required marker: {marker}")
        for marker in _REQUIRED_MARKERS[2:]:  # \tableofcontents, \maketitle — inject if missing
            if marker not in source:
                logger.warning("Missing %s — injecting after \\begin{document}", marker)
                source = source.replace(
                    r"\begin{document}", r"\begin{document}" + "\n" + marker, 1
                )
        return source

    def _save(self, source: str, filename: str) -> Path:
        out_dir = Path(RESULTS_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / filename
        path.write_text(source, encoding="utf-8")
        logger.info("Draft saved: %s (%d chars)", path, len(source))
        return path
