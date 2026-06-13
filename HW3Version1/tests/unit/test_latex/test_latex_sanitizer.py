"""Tests for latex/latex_sanitizer.py — basic fixes and utility functions."""
from __future__ import annotations

from pathlib import Path

import pytest

from article_writer.latex.latex_sanitizer import LatexSanitizer, _is_root_domain_url


def _s() -> LatexSanitizer:
    return LatexSanitizer()


# ── _is_root_domain_url ──────────────────────────────────────────────────────

def test_root_domain_url_bare_domain() -> None:
    assert _is_root_domain_url("https://example.com") is True


def test_root_domain_url_with_www() -> None:
    assert _is_root_domain_url("https://www.example.com") is True


def test_root_domain_url_trailing_slash() -> None:
    assert _is_root_domain_url("https://example.com/") is True


def test_root_domain_url_with_path() -> None:
    assert _is_root_domain_url("https://example.com/some/path") is False


def test_root_domain_url_no_scheme() -> None:
    assert _is_root_domain_url("example.com") is True


def test_root_domain_url_deep_link() -> None:
    assert _is_root_domain_url("https://www.who.int/health-topics/artificial-intelligence") is False


# ── _fix_wrong_main_language ─────────────────────────────────────────────────

def test_fix_main_language_corrects_hebrew() -> None:
    src = r"\setmainlanguage{hebrew}\setotherlanguage{english}"
    result, n = _s()._fix_wrong_main_language(src)
    assert r"\setmainlanguage{english}" in result
    assert n > 0


def test_fix_main_language_keeps_english() -> None:
    src = r"\setmainlanguage{english}\setotherlanguage{hebrew}"
    result, n = _s()._fix_wrong_main_language(src)
    assert result == src


def test_fix_main_language_corrects_other_lang() -> None:
    src = r"\setmainlanguage{english}\setotherlanguage{english}"
    result, n = _s()._fix_wrong_main_language(src)
    assert r"\setotherlanguage{hebrew}" in result
    assert n > 0


def test_fix_main_language_injects_headheight() -> None:
    src = r"\setmainlanguage{english}\setotherlanguage{hebrew}\usepackage{fancyhdr}"
    result, n = _s()._fix_wrong_main_language(src)
    assert r"\setlength{\headheight}" in result


def test_fix_main_language_no_headheight_if_already_present() -> None:
    src = (r"\setmainlanguage{english}\setotherlanguage{hebrew}"
           r"\usepackage{fancyhdr}\setlength{\headheight}{14pt}")
    result, n = _s()._fix_wrong_main_language(src)
    assert result.count(r"\setlength{\headheight}") == 1


# ── _fix_malformed_envs ──────────────────────────────────────────────────────

def test_fix_malformed_end_tag() -> None:
    src = r"\end{hebrew> " + "\n"
    result, n = _s()._fix_malformed_envs(src)
    assert r"\end{hebrew}" in result
    assert n > 0


def test_fix_html_close_tag() -> None:
    src = "</hebrew>"
    result, n = _s()._fix_malformed_envs(src)
    assert r"\end{hebrew}" in result
    assert n > 0


def test_fix_mixed_close_tag() -> None:
    src = "</hebrew}"
    result, n = _s()._fix_malformed_envs(src)
    assert r"\end{hebrew}" in result
    assert n > 0


def test_fix_tabularx_mismatch() -> None:
    src = r"\begin{tabularx}{\textwidth}{XX}content\end{tabular}"
    result, n = _s()._fix_malformed_envs(src)
    assert r"\end{tabularx}" in result
    assert n > 0


def test_fix_unclosed_axis() -> None:
    src = r"\begin{axis}[ybar]data\end{tikzpicture}"
    result, n = _s()._fix_malformed_envs(src)
    assert r"\end{axis}" in result
    assert n > 0


def test_fix_malformed_envs_no_change() -> None:
    src = r"\begin{hebrew}שלום\end{hebrew}"
    result, n = _s()._fix_malformed_envs(src)
    assert n == 0


# ── _fix_missing_bidi_envs ───────────────────────────────────────────────────

def test_fix_missing_bidi_envs_injects_when_absent() -> None:
    src = r"\begin{document}hello\end{document}"
    result, n = _s()._fix_missing_bidi_envs(src)
    assert r"\newenvironment{hebrewblock}" in result
    assert n == 1


def test_fix_missing_bidi_envs_no_change_when_present() -> None:
    src = r"\newenvironment{hebrewblock}{}{}\begin{document}hello\end{document}"
    result, n = _s()._fix_missing_bidi_envs(src)
    assert n == 0


# ── _fix_missing_ragged2e ────────────────────────────────────────────────────

def test_fix_missing_ragged2e_injects_when_absent() -> None:
    src = r"\usepackage{tabularx}"
    result, n = _s()._fix_missing_ragged2e(src)
    assert r"\usepackage{ragged2e}" in result
    assert n > 0


def test_fix_missing_ragged2e_no_change_when_present() -> None:
    src = r"\usepackage{ragged2e}\usepackage{tabularx}"
    result, n = _s()._fix_missing_ragged2e(src)
    # The typo-normalization regex also matches the correct form (replacing with itself),
    # so n may be 1. What matters is that ragged2e appears exactly once.
    assert result.count(r"\usepackage{ragged2e}") == 1


def test_fix_missing_ragged2e_fixes_typo() -> None:
    src = r"\usepackage{ragged2ce}\usepackage{tabularx}"
    result, n = _s()._fix_missing_ragged2e(src)
    assert r"\usepackage{ragged2e}" in result
    assert n > 0


def test_fix_missing_ragged2e_removes_duplicate() -> None:
    src = "\\usepackage{ragged2e}\n\\usepackage{ragged2e}\n"
    result, n = _s()._fix_missing_ragged2e(src)
    assert result.count(r"\usepackage{ragged2e}") == 1
    assert n > 0


# ── _fix_bidi_body_sections ──────────────────────────────────────────────────

def test_fix_bidi_body_wraps_hebrew() -> None:
    src = r"\end{titlepage}" + "\n\\begin{hebrew}שלום\\end{hebrew}"
    result, n = _s()._fix_bidi_body_sections(src)
    assert r"\begin{hebrewblock}" in result
    assert n > 0


def test_fix_bidi_body_wraps_english() -> None:
    src = r"\end{titlepage}" + "\n\\begin{english}Hello\\end{english}"
    result, n = _s()._fix_bidi_body_sections(src)
    assert r"\begin{englishblock}" in result
    assert n > 0


def test_fix_bidi_body_no_titlepage() -> None:
    src = r"\begin{hebrew}שלום\end{hebrew}"
    result, n = _s()._fix_bidi_body_sections(src)
    assert r"\begin{hebrewblock}" in result
    assert n > 0
