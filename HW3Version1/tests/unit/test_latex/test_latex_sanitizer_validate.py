"""Tests for LatexSanitizer.validate — post-compile validation logic."""
from __future__ import annotations

from pathlib import Path

from article_writer.latex.latex_sanitizer import LatexSanitizer


def _s() -> LatexSanitizer:
    return LatexSanitizer()


def _tex(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "draft.tex"
    p.write_text(content, encoding="utf-8")
    return p


# ── wrong main language ───────────────────────────────────────────────────────

def test_validate_critical_wrong_main_language(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\setmainlanguage{hebrew}")
    issues = _s().validate(p)
    assert any("CRITICAL" in i for i in issues)


def test_validate_no_wrong_main_language(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\setmainlanguage{english}")
    issues = _s().validate(p)
    assert not any("CRITICAL" in i for i in issues)


# ── malformed closing tags ────────────────────────────────────────────────────

def test_validate_detects_malformed_closing_tag(tmp_path: Path) -> None:
    p = _tex(tmp_path, "</hebrew>")
    issues = _s().validate(p)
    assert any("malformed" in i for i in issues)


def test_validate_no_malformed_closing_tag(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\begin{hebrew}שלום\end{hebrew}")
    issues = _s().validate(p)
    assert not any("malformed" in i for i in issues)


# ── bare hebrewfont in body ───────────────────────────────────────────────────

def test_validate_detects_bare_hebrewfont_in_body(tmp_path: Path) -> None:
    src = r"\end{titlepage}" + "\n\\hebrewfont שלום"
    p = _tex(tmp_path, src)
    issues = _s().validate(p)
    assert any("bare" in i and "hebrewfont" in i for i in issues)


def test_validate_texthebrew_is_ok(tmp_path: Path) -> None:
    src = r"\end{titlepage}" + "\n\\hebrewfont\\texthebrew{שלום}"
    p = _tex(tmp_path, src)
    issues = _s().validate(p)
    assert not any("hebrewfont" in i for i in issues)


# ── bare \begin{hebrew} in body ───────────────────────────────────────────────

def test_validate_detects_bare_begin_hebrew_in_body(tmp_path: Path) -> None:
    src = r"\end{titlepage}" + "\n\\begin{hebrew}שלום\\end{hebrew}"
    p = _tex(tmp_path, src)
    issues = _s().validate(p)
    assert any("begin{hebrew}" in i or "bare" in i for i in issues)


# ── missing hebrewblock env ───────────────────────────────────────────────────

def test_validate_detects_missing_hebrewblock(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\begin{document}\end{document}")
    issues = _s().validate(p)
    assert any("hebrewblock" in i for i in issues)


def test_validate_no_missing_hebrewblock(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    issues = _s().validate(p)
    assert not any("hebrewblock env not defined" in i for i in issues)


# ── biber log missing citations ───────────────────────────────────────────────

def test_validate_detects_missing_citation_from_blg(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    blg = tmp_path / "draft.blg"
    blg.write_text("WARN - I didn't find a database entry for 'fake_key_2024'", encoding="utf-8")
    issues = _s().validate(p, blg_path=blg)
    assert any("unresolved citation" in i for i in issues)


def test_validate_no_missing_citation_clean_blg(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    blg = tmp_path / "draft.blg"
    blg.write_text("INFO - all entries resolved", encoding="utf-8")
    issues = _s().validate(p, blg_path=blg)
    assert not any("unresolved citation" in i for i in issues)


# ── lualatex log font errors and undefined refs ───────────────────────────────

def test_validate_detects_font_error_from_log(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    log = tmp_path / "draft.log"
    log.write_text("Error: font not found for 'David Libre'", encoding="utf-8")
    issues = _s().validate(p, log_path=log)
    assert any("font-not-found" in i for i in issues)


def test_validate_detects_undefined_ref(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    log = tmp_path / "draft.log"
    log.write_text(
        "LaTeX Warning: Reference `fig:accuracy' on page 3 undefined", encoding="utf-8"
    )
    issues = _s().validate(p, log_path=log)
    assert any("undefined" in i and "ref" in i.lower() for i in issues)


def test_validate_detects_undefined_cite(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    log = tmp_path / "draft.log"
    log.write_text(
        "Package biblatex Warning: Citation 'aha.org' on page 4 undefined", encoding="utf-8"
    )
    issues = _s().validate(p, log_path=log)
    assert any("cite" in i.lower() for i in issues)


# ── root-domain URLs in references.bib ───────────────────────────────────────

def test_validate_detects_root_domain_url_in_bib(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    bib = tmp_path / "references.bib"
    bib.write_text("@misc{x, url = {https://example.com}}", encoding="utf-8")
    issues = _s().validate(p)
    assert any("root-domain" in i for i in issues)


def test_validate_no_root_domain_url_with_deep_link(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    bib = tmp_path / "references.bib"
    bib.write_text("@misc{x, url = {https://example.com/some/path}}", encoding="utf-8")
    issues = _s().validate(p)
    assert not any("root-domain" in i for i in issues)


# ── clean document ────────────────────────────────────────────────────────────

def test_validate_clean_document_no_warnings(tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\newenvironment{hebrewblock}{}{}\begin{document}\end{document}")
    issues = _s().validate(p)
    assert not any("CRITICAL" in i or "WARN" in i for i in issues)
