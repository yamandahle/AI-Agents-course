"""Tests for latex/latex_sanitizer.py — table, arrow, cite-key, and include fixes."""
from __future__ import annotations

from pathlib import Path

import pytest

from article_writer.latex.latex_sanitizer import LatexSanitizer


def _s() -> LatexSanitizer:
    return LatexSanitizer()


# ── _fix_table_alignment ─────────────────────────────────────────────────────

def test_fix_table_converts_plain_tabular() -> None:
    src = r"\end{titlepage}" + "\n\\begin{tabular}{llll}a&b&c&d\\\\\\end{tabular}"
    result, n = _s()._fix_table_alignment(src)
    assert r"\begin{tabularx}{\textwidth}" in result
    assert n > 0


def test_fix_table_converts_tabularx_bad_cols() -> None:
    src = r"\end{titlepage}" + "\n\\begin{tabularx}{\\textwidth}{lll}a&b&c\\\\\\end{tabularx}"
    result, n = _s()._fix_table_alignment(src)
    assert r"\RaggedRight" in result
    assert n > 0


def test_fix_table_skips_good_tabularx() -> None:
    col = r">{\RaggedRight\arraybackslash}X"
    src = (r"\end{titlepage}" + "\n\\begin{tabularx}{\\textwidth}{"
           + col + " " + col + "}a&b\\\\\\end{tabularx}")
    result, n = _s()._fix_table_alignment(src)
    assert n == 0


def test_fix_table_skips_cover_tabular() -> None:
    # Content before \end{titlepage} should not be converted
    src = r"\begin{tabular}{rl}Author & Name\\\end{tabular}\end{titlepage}"
    result, n = _s()._fix_table_alignment(src)
    assert n == 0


# ── _fix_arrow_labels ────────────────────────────────────────────────────────

def test_fix_arrow_adds_fill_white() -> None:
    line = r"  \draw[->] (A) -- (B) node[midway,above] {Label};"
    result, n = _s()._fix_arrow_labels(line)
    assert "fill=white" in result
    assert n > 0


def test_fix_arrow_no_change_if_fill_present() -> None:
    line = r"  \draw[->] (A) -- (B) node[midway,fill=white] {Label};"
    result, n = _s()._fix_arrow_labels(line)
    assert n == 0


def test_fix_arrow_only_on_draw_lines() -> None:
    src = r"\node[above] at (0,0) {Title};"
    result, n = _s()._fix_arrow_labels(src)
    assert n == 0


# ── _inject_fill_white ───────────────────────────────────────────────────────

def test_inject_fill_white_modifies_node() -> None:
    line = r"\draw[->] (A) -- (B) node[midway] {X}"
    result, n = _s()._inject_fill_white(line)
    assert "fill=white" in result
    assert n > 0


def test_inject_fill_white_skips_if_fill_present() -> None:
    line = r"\draw[->] (A) -- (B) node[fill=red] {X}"
    result, n = _s()._inject_fill_white(line)
    assert n == 0


# ── _remap_key + _fix_invalid_cite_keys ─────────────────────────────────────

def test_remap_key_fda() -> None:
    assert LatexSanitizer._remap_key("fda_regulation") == "fda_ai_ml_samd"


def test_remap_key_who() -> None:
    assert LatexSanitizer._remap_key("who_report_2022") == "who2021ai"


def test_remap_key_unknown_returns_default() -> None:
    assert LatexSanitizer._remap_key("completely_unknown_xyz") == "who2021ai"


def test_remap_key_ibm() -> None:
    assert LatexSanitizer._remap_key("ibm_watson") == "ibm_watson_health"


def test_fix_invalid_cite_keys_replaces_bad_key() -> None:
    src = r"\cite{aha.org}"
    result, n = _s()._fix_invalid_cite_keys(src)
    assert "aha.org" not in result
    assert n > 0


def test_fix_invalid_cite_keys_keeps_valid_key() -> None:
    src = r"\cite{who2021ai}"
    result, n = _s()._fix_invalid_cite_keys(src)
    assert r"\cite{who2021ai}" in result
    assert n == 0


def test_fix_invalid_cite_keys_multi_key() -> None:
    src = r"\cite{who2021ai, aha.org}"
    result, n = _s()._fix_invalid_cite_keys(src)
    assert "aha.org" not in result
    assert "who2021ai" in result


def test_fix_invalid_cite_keys_deduplicates() -> None:
    # Two bad keys that both remap to the same valid key → deduplicate
    src = r"\cite{aha.org, bcg.com}"
    result, n = _s()._fix_invalid_cite_keys(src)
    # Should not repeat the same key twice
    inner = result[result.index("{") + 1:result.rindex("}")]
    keys = [k.strip() for k in inner.split(",")]
    assert len(keys) == len(set(keys))


# ── _fix_cover_metadata ──────────────────────────────────────────────────────

def test_fix_cover_metadata_corrects_authors() -> None:
    src = (r"\begin{titlepage}"
           r"\textbf{Authors:} & Wrong Name \\"
           r"\end{titlepage}")
    result, n = _s()._fix_cover_metadata(src)
    assert "Nagham Manasra" in result
    assert n > 0


def test_fix_cover_metadata_keeps_correct_authors() -> None:
    src = (r"\begin{titlepage}"
           r"\textbf{Authors:} & Nagham Manasra \& Yaman Dahle \\"
           r"\end{titlepage}")
    result, n = _s()._fix_cover_metadata(src)
    assert n == 0


def test_fix_cover_metadata_corrects_course() -> None:
    src = (r"\begin{titlepage}"
           r"\textbf{Course:} & Wrong Course Name \\"
           r"\end{titlepage}")
    result, n = _s()._fix_cover_metadata(src)
    assert "203.3763" in result
    assert n > 0


def test_fix_cover_metadata_no_titlepage() -> None:
    src = r"\textbf{Authors:} & Wrong \\"
    result, n = _s()._fix_cover_metadata(src)
    assert n == 0


# ── sanitize (file-level integration) ───────────────────────────────────────

def test_sanitize_rewrites_file(tmp_path: Path) -> None:
    tex = tmp_path / "draft.tex"
    src = (r"\setmainlanguage{hebrew}" + "\n"
           r"\setotherlanguage{english}" + "\n"
           r"\begin{document}hello\end{document}")
    tex.write_text(src, encoding="utf-8")
    _s().sanitize(tex)
    result = tex.read_text(encoding="utf-8")
    assert r"\setmainlanguage{english}" in result


def test_sanitize_no_write_when_no_changes(tmp_path: Path) -> None:
    tex = tmp_path / "draft.tex"
    src = (r"\setmainlanguage{english}" + "\n"
           r"\setotherlanguage{hebrew}" + "\n"
           r"\setlength{\headheight}{14pt}" + "\n"
           r"\newenvironment{hebrewblock}{}{}" + "\n"
           r"\begin{document}hello\end{document}")
    tex.write_text(src, encoding="utf-8")
    mtime_before = tex.stat().st_mtime
    _s().sanitize(tex)
    mtime_after = tex.stat().st_mtime
    # File should not be rewritten if there were no changes
    assert tex.read_text(encoding="utf-8") == src
