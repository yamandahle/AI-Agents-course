"""Tests for latex/latex_compiler.py — lualatex multi-pass compiler."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch, call
import subprocess

import pytest

from article_writer.latex.latex_compiler import LaTeXCompiler, CompilationError


def _make_compiler() -> LaTeXCompiler:
    mock_cfg = MagicMock()
    mock_cfg.latex.compiler = "lualatex"
    mock_cfg.latex.compile_passes = 3
    with patch("article_writer.latex.latex_compiler.load_config", return_value=mock_cfg):
        return LaTeXCompiler()


def test_extract_page_count_parses_log(tmp_path: Path) -> None:
    log = tmp_path / "article.log"
    log.write_text("Output written on article.pdf (17 pages, 123456 bytes).", encoding="utf-8")
    compiler = _make_compiler()
    assert compiler._extract_page_count(log) == 17


def test_extract_page_count_returns_zero_on_missing_file(tmp_path: Path) -> None:
    compiler = _make_compiler()
    assert compiler._extract_page_count(tmp_path / "nonexistent.log") == 0


def test_extract_page_count_returns_zero_on_no_match(tmp_path: Path) -> None:
    log = tmp_path / "article.log"
    log.write_text("This log has no output line.", encoding="utf-8")
    compiler = _make_compiler()
    assert compiler._extract_page_count(log) == 0


def test_run_pass_logs_warning_on_nonzero_exit(tmp_path: Path) -> None:
    # _run_pass intentionally only warns on non-zero exit — CompilationError is
    # raised by compile() when the PDF is absent after all passes.
    compiler = _make_compiler()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "LaTeX error"
    with patch("subprocess.run", return_value=mock_result):
        compiler._run_pass(["lualatex", "article.tex"], tmp_path)  # must not raise


def test_run_pass_succeeds_on_zero_exit(tmp_path: Path) -> None:
    compiler = _make_compiler()
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        compiler._run_pass(["lualatex", "article.tex"], tmp_path)


def test_compile_raises_when_pdf_missing(tmp_path: Path) -> None:
    compiler = _make_compiler()
    tex_file = tmp_path / "article.tex"
    tex_file.write_text(r"\documentclass{article}\begin{document}\end{document}", encoding="utf-8")
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(CompilationError, match="PDF not produced"):
            compiler.compile(tex_file, tmp_path)
