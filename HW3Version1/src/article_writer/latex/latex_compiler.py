"""LaTeX compiler — runs lualatex (N passes) + biber, validates page count."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from article_writer.shared.config import load_config
from article_writer.shared.constants import DEFAULT_ENCODING, MIN_ARTICLE_PAGES
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)


class CompilationError(Exception):
    """Raised when lualatex or biber exits with a non-zero status."""


class LaTeXCompiler:
    """Compiles a .tex file to PDF using lualatex (multi-pass) + biber."""

    def __init__(self) -> None:
        cfg = load_config()
        self._compiler = cfg.latex.compiler
        self._passes = cfg.latex.compile_passes

    def compile(self, tex_path: Path, output_dir: Path | None = None) -> Path:
        """Compile tex_path to PDF. Returns path to resulting .pdf."""
        cwd = output_dir or tex_path.parent
        stem = tex_path.stem
        self._run_pass([self._compiler, "-interaction=nonstopmode", str(tex_path)], cwd)
        self._run_pass(["biber", stem], cwd)
        for _ in range(self._passes - 1):
            self._run_pass([self._compiler, "-interaction=nonstopmode", str(tex_path)], cwd)
        pdf_path = cwd / f"{stem}.pdf"
        if not pdf_path.exists():
            raise CompilationError(f"PDF not produced at {pdf_path}")
        log_path = cwd / f"{stem}.log"
        pages = self._extract_page_count(log_path)
        logger.info("Compilation complete: %d pages — %s", pages, pdf_path)
        if pages < MIN_ARTICLE_PAGES:
            logger.warning("PDF has %d pages; target is %d — consider expanding the draft",
                           pages, MIN_ARTICLE_PAGES)
        return pdf_path

    def _run_pass(self, cmd: list[str], cwd: Path) -> None:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            # lualatex still produces PDF on non-fatal errors; biber warns on missing entries.
            # Only hard-fail when no PDF is produced (checked after all passes).
            logger.warning("%s exited %d — %s", cmd[0], result.returncode,
                           (result.stderr or result.stdout)[-200:].strip())
        else:
            logger.info("Pass completed: %s", " ".join(cmd[:2]))

    def _extract_page_count(self, log_path: Path) -> int:
        try:
            log = log_path.read_text(encoding=DEFAULT_ENCODING, errors="replace")
            match = re.search(r"Output written on .+\((\d+) page", log)
            return int(match.group(1)) if match else 0
        except FileNotFoundError:
            return 0
