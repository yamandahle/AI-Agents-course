"""Tests for TikZ spatial-collision sanitizer fixes (Fix 9 edge cases + Fix 12)."""
from __future__ import annotations

from article_writer.latex.latex_sanitizer import LatexSanitizer


def _s() -> LatexSanitizer:
    return LatexSanitizer()


# ── Fix 12: _fix_diagonal_paths ──────────────────────────────────────────────

def test_fix_diagonal_paths_converts_diagonal() -> None:
    """A diagonal ++(x,y) segment is split into two orthogonal segments."""
    src = r"\draw[->] (A) -- ++(2cm,-3cm) -- (B);"
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 1
    assert "-- ++(2cm,0) -- ++(0,-3cm)" in result
    # Original diagonal gone
    assert "++(2cm,-3cm)" not in result


def test_fix_diagonal_paths_converts_positive_positive() -> None:
    src = r"\draw[->] (start.east) -- ++(1.5cm,2cm);"
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 1
    assert "-- ++(1.5cm,0) -- ++(0,2cm)" in result


def test_fix_diagonal_paths_skips_orthogonal_x_only() -> None:
    """++(3cm,0) is already axis-aligned — must not be changed."""
    src = r"\draw[->] (A) -- ++(3cm,0) |- (B);"
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 0
    assert result == src


def test_fix_diagonal_paths_skips_zero_y() -> None:
    """-- ++(0,-2cm) is vertical — must not be changed."""
    src = r"\draw[->] (A) -- ++(0,-2cm);"
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 0
    assert result == src


def test_fix_diagonal_paths_skips_zero_x() -> None:
    src = r"\draw[->] (A) -- ++(0,1.5cm);"
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 0
    assert result == src


def test_fix_diagonal_paths_multiple_segments() -> None:
    """Multiple diagonal segments in one source — all converted."""
    src = (
        r"\draw[->] (A) -- ++(2cm,-1cm);" + "\n"
        r"\draw[->] (B) -- ++(3cm,1.5cm);"
    )
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 2


def test_fix_diagonal_paths_no_tikz_no_change() -> None:
    src = "Plain text without any draw commands."
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 0
    assert result == src


def test_fix_diagonal_paths_unitless_numbers() -> None:
    """Coordinates without units (e.g., ++(2,3)) are also converted."""
    src = r"\draw[->] (A) -- ++(2,3);"
    result, n = _s()._fix_diagonal_paths(src)
    assert n == 1
    assert "-- ++(2,0) -- ++(0,3)" in result


# ── Fix 9: _fix_arrow_labels (edge cases) ────────────────────────────────────

def test_fix_arrow_labels_to_syntax() -> None:
    """Edge label on a \draw[->] (A) to (B) path also gets fill=white."""
    src = r"\draw[->] (A) to (B) node[midway, above] {Signal};"
    result, n = _s()._fix_arrow_labels(src)
    assert n == 1
    assert "fill=white" in result


def test_fix_arrow_labels_already_has_fill_unchanged() -> None:
    src = r"\draw[->] (A) -- (B) node[midway, fill=blue!20, inner sep=2pt] {Ok};"
    result, n = _s()._fix_arrow_labels(src)
    assert n == 0
    assert result == src


def test_fix_arrow_labels_injects_on_multi_hop() -> None:
    """Multi-hop path with a naked midway node still gets fill=white."""
    src = r"\draw[->] (A) -- (B) -- (C) node[midway, above] {Flow};"
    result, n = _s()._fix_arrow_labels(src)
    assert n == 1
    assert "fill=white" in result
