"""Extra targeted tests to cover remaining sanitizer branches."""
from __future__ import annotations

from pathlib import Path

from article_writer.latex.latex_sanitizer import LatexSanitizer
from article_writer.tools.chart_checker import _build_draft_series, _align_table_rows


def _s() -> LatexSanitizer:
    return LatexSanitizer()


# ── _escape_node_amp inside _fix_malformed_envs ──────────────────────────────

def test_fix_malformed_envs_escapes_ampersand_in_node_label() -> None:
    src = r"\node[box] {Label & Value}"
    result, n = _s()._fix_malformed_envs(src)
    assert r"\&" in result
    assert n > 0


# ── _fix_includegraphics ──────────────────────────────────────────────────────

def test_fix_includegraphics_replaces_chart_image() -> None:
    src = (r"\begin{figure}[H]" + "\n"
           r"\includegraphics{accuracy_chart.png}" + "\n"
           r"\caption{Accuracy comparison of models.}" + "\n"
           r"\end{figure}")
    result, n = _s()._fix_includegraphics(src)
    assert r"\begin{axis}" in result
    assert n > 0


def test_fix_includegraphics_replaces_non_chart_image() -> None:
    src = (r"\begin{figure}[H]" + "\n"
           r"\includegraphics{hospital_photo.png}" + "\n"
           r"\caption{Hospital overview.}" + "\n"
           r"\end{figure}")
    result, n = _s()._fix_includegraphics(src)
    assert r"\begin{tikzpicture}" in result
    assert n > 0


def test_fix_includegraphics_skips_logo() -> None:
    src = (r"\begin{figure}[H]" + "\n"
           r"\includegraphics[width=5cm]{../assets/images/uniHaifasymbol.png}" + "\n"
           r"\end{figure}")
    result, n = _s()._fix_includegraphics(src)
    assert "uniHaifasymbol" in result
    assert n == 0


def test_fix_includegraphics_no_figure_no_change() -> None:
    src = r"No figure blocks here."
    result, n = _s()._fix_includegraphics(src)
    assert n == 0


# ── _fix_cover_hebrew ─────────────────────────────────────────────────────────

def test_fix_cover_hebrew_single_line_hebrewfont() -> None:
    src = (r"\begin{titlepage}" + "\n"
           "  {\\hebrewfont\\large כותרת בעברית\\par}\n"
           r"\end{titlepage}")
    result, n = _s()._fix_cover_hebrew(src)
    assert r"\begin{hebrew}" in result
    assert n > 0


def test_fix_cover_hebrew_no_hebrew_text_no_change() -> None:
    src = (r"\begin{titlepage}" + "\n"
           r"  {\hebrewfont\large Latin only\par}" + "\n"
           r"\end{titlepage}")
    result, n = _s()._fix_cover_hebrew(src)
    assert n == 0


def test_fix_cover_hebrew_already_wrapped_no_change() -> None:
    src = (r"\begin{titlepage}" + "\n"
           "  {\\hebrewfont\\large\\begin{hebrew}כותרת\\end{hebrew}\\par}\n"
           r"\end{titlepage}")
    result, n = _s()._fix_cover_hebrew(src)
    assert n == 0


# ── _build_draft_series (chart_checker) ──────────────────────────────────────

def test_build_draft_series_empty() -> None:
    result = _build_draft_series([])
    assert result == ""


def test_build_draft_series_single_series() -> None:
    series = [{"name": "AI", "coords": {"A": 94.0, "B": 90.0}}]
    result = _build_draft_series(series)
    assert r"\addplot+" in result
    assert "(A,94.0)" in result


# ── _align_table_rows (chart_checker) ────────────────────────────────────────

def test_align_table_rows_empty() -> None:
    result = _align_table_rows([])
    assert "no tick labels" in result


def test_align_table_rows_pass() -> None:
    result = _align_table_rows([("Label A", True)])
    assert "PASS" in result
    assert "Label A" in result


def test_align_table_rows_fail() -> None:
    result = _align_table_rows([("Label B", False)])
    assert "FAIL" in result
    assert "Label B" in result
