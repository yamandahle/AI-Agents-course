"""Tests for chart_generator — matplotlib PDF generation."""
from __future__ import annotations

from pathlib import Path

import pytest

from article_writer.tools.chart_generator import (
    generate_accuracy_curve,
    generate_all,
    generate_cost_reduction,
    generate_diagnostic_comparison,
)


# ── individual generators ─────────────────────────────────────────────────────

def test_generate_accuracy_curve_creates_pdf(tmp_path: Path) -> None:
    out = generate_accuracy_curve(tmp_path)
    assert out.exists()
    assert out.suffix == ".pdf"
    assert out.name == "accuracy_curve.pdf"
    assert out.stat().st_size > 1000


def test_generate_diagnostic_comparison_creates_pdf(tmp_path: Path) -> None:
    out = generate_diagnostic_comparison(tmp_path)
    assert out.exists()
    assert out.name == "diagnostic_comparison.pdf"
    assert out.stat().st_size > 1000


def test_generate_cost_reduction_creates_pdf(tmp_path: Path) -> None:
    out = generate_cost_reduction(tmp_path)
    assert out.exists()
    assert out.name == "cost_reduction.pdf"
    assert out.stat().st_size > 1000


# ── generate_all ─────────────────────────────────────────────────────────────

def test_generate_all_returns_three_paths(tmp_path: Path) -> None:
    paths = generate_all(tmp_path)
    assert len(paths) == 3
    for p in paths:
        assert p.exists()
        assert p.suffix == ".pdf"


def test_generate_all_creates_out_dir(tmp_path: Path) -> None:
    new_dir = tmp_path / "graphs" / "sub"
    paths = generate_all(new_dir)
    assert new_dir.exists()
    assert len(paths) == 3


def test_generate_all_skips_existing_by_default(tmp_path: Path) -> None:
    """Second call without regenerate=True must not re-create existing files."""
    paths_first = generate_all(tmp_path)
    mtimes_first = [p.stat().st_mtime for p in paths_first]

    paths_second = generate_all(tmp_path)
    mtimes_second = [p.stat().st_mtime for p in paths_second]

    assert mtimes_first == mtimes_second


def test_generate_all_regenerates_when_flag_set(tmp_path: Path) -> None:
    """regenerate=True must overwrite existing files (mtime changes)."""
    generate_all(tmp_path)
    mtimes_first = [(tmp_path / n).stat().st_mtime for n in (
        "accuracy_curve.pdf", "diagnostic_comparison.pdf", "cost_reduction.pdf"
    )]

    import time
    time.sleep(0.05)
    generate_all(tmp_path, regenerate=True)
    mtimes_second = [(tmp_path / n).stat().st_mtime for n in (
        "accuracy_curve.pdf", "diagnostic_comparison.pdf", "cost_reduction.pdf"
    )]

    assert mtimes_second > mtimes_first


def test_generate_all_file_names(tmp_path: Path) -> None:
    paths = generate_all(tmp_path)
    names = {p.name for p in paths}
    assert names == {"accuracy_curve.pdf", "diagnostic_comparison.pdf", "cost_reduction.pdf"}
