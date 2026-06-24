"""T597–T619: Unit tests for Plotter and ReportGenerator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from hw5.services.cell_result import CellResult
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.plotter import Plotter
from hw5.services.report import ReportGenerator
from hw5.services.runner_protocol import InferenceResult

# ── helpers ───────────────────────────────────────────────────────────────────


def _snap(
    ram: float = 400.0,
    vram: float = 0.0,
    swap: float = 0.0,
    samples: list | None = None,
) -> MetricsSnapshot:
    return MetricsSnapshot(
        samples=samples or [],
        spike_events=[],
        peak_ram_mb=ram,
        peak_vram_mb=vram,
        peak_swap_mb=swap,
        avg_cpu_pct=30.0,
        total_disk_read_mb=0.0,
    )


def _ir(framework: str, quant: str, tps: float) -> InferenceResult:
    return InferenceResult(
        output_text="ok",
        tokens_generated=int(tps),
        total_time_s=1.0,
        first_token_latency_s=0.1,
        framework=framework,
        model_id="test",
        quant=quant,
    )


def _cell(
    cell_id: str,
    tps: float = 10.0,
    ram: float = 300.0,
    failed: bool = False,
    samples: list | None = None,
) -> CellResult:
    p = cell_id.split("__")
    return CellResult(
        cell_id=cell_id,
        inference=_ir(p[1], p[2], tps),
        metrics=_snap(ram=ram, samples=samples),
        started_at=0.0,
        finished_at=1.0,
        failed=failed,
    )


_SAMPLES = [
    {"ts": 0.0, "ram": 300.0},
    {"ts": 0.5, "ram": 350.0},
    {"ts": 1.0, "ram": 320.0},
]

RESULTS = [
    _cell("model_a__ollama__Q4", tps=20.0, ram=400.0, samples=_SAMPLES),
    _cell("model_a__airllm__Q4", tps=15.0, ram=300.0, samples=_SAMPLES),
    _cell("model_a__ollama__Q8", tps=18.0, ram=500.0),
    _cell("model_b__ollama__Q4", tps=25.0, ram=200.0),
    _cell("model_b__airllm__Q8", tps=12.0, ram=180.0),
    _cell("model_b__ollama__Q4", tps=0.0, ram=100.0, failed=True),  # failed — excluded
]


@pytest.fixture
def plotter(config) -> Plotter:
    return Plotter(RESULTS, config)


# ── T597: _get_df columns ──────────────────────────────────────────────────────


def test_get_df_has_expected_columns(plotter: Plotter):
    df = plotter._get_df()
    expected = {
        "model",
        "framework",
        "quant",
        "tokens_per_sec",
        "peak_ram_mb",
        "peak_vram_mb",
        "peak_swap_mb",
        "avg_cpu_pct",
        "failed",
    }
    assert set(df.columns) == expected


# ── T603: failed cells excluded ────────────────────────────────────────────────


def test_get_df_excludes_failed_cells(plotter: Plotter):
    df = plotter._get_df()
    assert df["failed"].sum() == 0
    assert len(df) == len([r for r in RESULTS if not r.failed])


# ── T598: heatmap ─────────────────────────────────────────────────────────────


def test_heatmap_returns_figure(plotter: Plotter):
    from matplotlib.figure import Figure

    fig = plotter.heatmap()
    assert isinstance(fig, Figure)


# ── T599: ram_timeline ────────────────────────────────────────────────────────


def test_ram_timeline_returns_figure(plotter: Plotter):
    from matplotlib.figure import Figure

    fig = plotter.ram_timeline()
    assert isinstance(fig, Figure)


def test_ram_timeline_skips_cells_without_samples(plotter: Plotter):
    from matplotlib.figure import Figure

    results_no_samples = [_cell("model_a__ollama__Q4", tps=10.0)]
    p = Plotter(results_no_samples, plotter._config)
    fig = p.ram_timeline()
    assert isinstance(fig, Figure)


# ── T600: vram_bar_chart ──────────────────────────────────────────────────────


def test_vram_bar_chart_returns_figure(plotter: Plotter):
    from matplotlib.figure import Figure

    fig = plotter.vram_bar_chart()
    assert isinstance(fig, Figure)


def test_vram_bar_chart_returns_figure_on_empty_df(config):
    from matplotlib.figure import Figure

    p = Plotter([_cell("x__ollama__Q4", failed=True)], config)
    fig = p.vram_bar_chart()
    assert isinstance(fig, Figure)


# ── T601: tradeoff_scatter ────────────────────────────────────────────────────


def test_tradeoff_scatter_returns_figure(plotter: Plotter):
    from matplotlib.figure import Figure

    fig = plotter.tradeoff_scatter()
    assert isinstance(fig, Figure)


# ── T604: _find_pareto_front ──────────────────────────────────────────────────


def test_find_pareto_front_returns_correct_subset():
    df = pd.DataFrame(
        [
            {
                "model": "a",
                "framework": "ollama",
                "quant": "Q4",
                "tokens_per_sec": 20.0,
                "peak_ram_mb": 100.0,
                "peak_vram_mb": 0.0,
                "peak_swap_mb": 0.0,
                "avg_cpu_pct": 50.0,
                "failed": False,
            },
            {
                "model": "b",
                "framework": "airllm",
                "quant": "Q8",
                "tokens_per_sec": 15.0,
                "peak_ram_mb": 150.0,
                "peak_vram_mb": 0.0,
                "peak_swap_mb": 0.0,
                "avg_cpu_pct": 40.0,
                "failed": False,
            },
            {
                "model": "c",
                "framework": "ollama",
                "quant": "Q4",
                "tokens_per_sec": 10.0,
                "peak_ram_mb": 80.0,
                "peak_vram_mb": 0.0,
                "peak_swap_mb": 0.0,
                "avg_cpu_pct": 30.0,
                "failed": False,
            },
        ]
    )
    pareto = Plotter._find_pareto_front(df)
    assert len(pareto) == 2
    assert set(pareto["model"]) == {"a", "c"}


def test_find_pareto_front_empty_df():
    assert Plotter._find_pareto_front(pd.DataFrame()).empty


# ── T602: save_all ────────────────────────────────────────────────────────────


def test_save_all_returns_eight_paths(plotter: Plotter, tmp_path: Path):
    plotter._config.assets_dir = str(tmp_path / "assets")
    paths = plotter.save_all()
    assert len(paths) == 8
    assert all(p.exists() for p in paths)
    exts = {p.suffix for p in paths}
    assert exts == {".png", ".svg"}


# ── T619: save_csv ────────────────────────────────────────────────────────────


def test_save_csv_produces_valid_csv_with_correct_columns(
    plotter: Plotter, tmp_path: Path
):
    import csv

    out = tmp_path / "results.csv"
    path = plotter.save_csv(out)
    assert path.exists()
    rows = list(csv.DictReader(path.read_text().splitlines()))
    assert len(rows) > 0
    assert "tokens_per_sec" in rows[0]
    assert "peak_ram_mb" in rows[0]


# ── T609: ReportGenerator.to_html ─────────────────────────────────────────────


def test_to_html_contains_all_four_section_ids(tmp_path: Path):
    summaries = {
        "heatmap": "heatmap summary",
        "ram_timeline": "timeline summary",
        "vram_bar": "vram summary",
        "tradeoff_scatter": "scatter summary",
    }
    plot_paths: dict[str, Path] = {}
    gen = ReportGenerator(summaries, plot_paths, RESULTS)
    html = gen.to_html()
    for section_id in ("heatmap", "ram_timeline", "vram_bar", "tradeoff_scatter"):
        assert f'id="{section_id}"' in html


def test_to_html_embeds_existing_png_as_base64(tmp_path: Path):
    png = tmp_path / "heatmap.png"
    png.write_bytes(b"\x89PNG\r\n")
    summaries = {"heatmap": "a"}
    gen = ReportGenerator(summaries, {"heatmap.png": png}, RESULTS)
    html = gen.to_html()
    assert "data:image/png;base64," in html


def test_report_save_writes_html_file(tmp_path: Path):
    gen = ReportGenerator({"heatmap": "x"}, {}, RESULTS)
    path = gen.save(tmp_path / "report.html")
    assert path.exists()
    assert path.read_text().startswith("<!DOCTYPE html>")
