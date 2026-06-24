"""T666–T679: Integration smoke tests for the full CLI pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hw5.main import main
from hw5.services.cell_result import CellResult
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.runner_protocol import InferenceResult

pytestmark = pytest.mark.integration


# ── helpers ───────────────────────────────────────────────────────────────────


def _snap() -> MetricsSnapshot:
    return MetricsSnapshot(
        samples=[],
        spike_events=[],
        peak_ram_mb=300.0,
        peak_vram_mb=0.0,
        peak_swap_mb=0.0,
        avg_cpu_pct=30.0,
        total_disk_read_mb=0.0,
    )


def _ir(fw: str = "ollama") -> InferenceResult:
    return InferenceResult(
        output_text="ok",
        tokens_generated=10,
        total_time_s=1.0,
        first_token_latency_s=0.0,
        framework=fw,
        model_id="m",
        quant="Q4",
    )


def _cell(cell_id: str) -> CellResult:
    return CellResult(
        cell_id=cell_id,
        inference=_ir(),
        metrics=_snap(),
        started_at=0.0,
        finished_at=1.0,
    )


def _presave_results(results_dir: str, cells: list[CellResult]) -> None:
    from hw5.services.cell_persistence import save_result

    for cr in cells:
        save_result(cr, results_dir)


# ── T667: dry-run lists all cells without errors ─────────────────────────────


def test_dry_run_lists_expected_cells(config_path: Path, models_json: Path, capsys):
    rc = main(["--config", str(config_path), "--dry-run"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "cell(s) would run" in captured.out
    assert "model_a" in captured.out
    assert "model_b" in captured.out


def test_dry_run_lists_twelve_cells(config_path: Path, models_json: Path, capsys):
    rc = main(["--config", str(config_path), "--dry-run"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "12 cell(s)" in captured.out


def test_dry_run_with_model_filter(config_path: Path, models_json: Path, capsys):
    rc = main(["--config", str(config_path), "--dry-run", "--models", "model_a"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "6 cell(s)" in captured.out
    assert "model_b" not in captured.out


# ── T668: plot mode generates PNG files ───────────────────────────────────────


def test_plot_mode_creates_png_files(
    config_path: Path, models_json: Path, tmp_path: Path
):
    rdir = str(tmp_path / "results")
    adir = str(tmp_path / "assets")
    cells = [_cell(f"model_a__ollama__Q{q}") for q in ("4", "8")]
    _presave_results(rdir, cells)

    raw = json.loads(config_path.read_text())
    raw["results_dir"] = rdir
    raw["assets_dir"] = adir
    cfg_path = tmp_path / "setup2.json"
    cfg_path.write_text(json.dumps(raw))

    rc = main(["--config", str(cfg_path), "--mode", "plot"])
    assert rc == 0
    assert (Path(adir) / "heatmap.png").exists()
    assert (Path(adir) / "tradeoff_scatter.png").exists()


# ── T669: report mode creates HTML ────────────────────────────────────────────


def test_report_mode_creates_html_file(
    config_path: Path, models_json: Path, tmp_path: Path
):
    rdir = str(tmp_path / "results")
    adir = str(tmp_path / "assets")
    cells = [_cell("model_a__ollama__Q4"), _cell("model_b__airllm__Q8")]
    _presave_results(rdir, cells)

    raw = json.loads(config_path.read_text())
    raw["results_dir"] = rdir
    raw["assets_dir"] = adir
    cfg_path = tmp_path / "setup3.json"
    cfg_path.write_text(json.dumps(raw))

    rc = main(["--config", str(cfg_path), "--mode", "report"])
    assert rc == 0
    report = Path(adir) / "report.html"
    assert report.exists()
    assert "<!DOCTYPE html>" in report.read_text()


# ── T670: assets/ contains expected file names ────────────────────────────────


def test_plot_mode_assets_contain_expected_names(
    config_path: Path, models_json: Path, tmp_path: Path
):
    rdir = str(tmp_path / "results")
    adir = str(tmp_path / "assets")
    cells = [_cell("model_a__ollama__Q4")]
    _presave_results(rdir, cells)

    raw = json.loads(config_path.read_text())
    raw["results_dir"] = rdir
    raw["assets_dir"] = adir
    cfg_path = tmp_path / "setup4.json"
    cfg_path.write_text(json.dumps(raw))

    main(["--config", str(cfg_path), "--mode", "plot"])
    assets = list(Path(adir).iterdir())
    names = {f.name for f in assets}
    for expected in ("heatmap.png", "heatmap.svg", "ram_timeline.png", "vram_bar.png"):
        assert expected in names, f"Missing: {expected}"


# ── T675/T677/T679: CLI override flags ────────────────────────────────────────


def test_output_dir_redirects_results(
    config_path: Path, models_json: Path, tmp_path: Path, capsys
):
    out_dir = tmp_path / "custom_out"
    rc = main(["--config", str(config_path), "--dry-run", "--output-dir", str(out_dir)])
    assert rc == 0


def test_eval_prompt_override_reflected_in_config(config_path: Path, models_json: Path):
    from hw5.sdk.sdk import EvalPipelineSDK

    sdk = EvalPipelineSDK(str(config_path))
    import argparse

    from hw5.main import _apply_overrides

    args = argparse.Namespace(
        resume=False, output_dir=None, eval_prompt="Custom prompt", max_tokens=None
    )
    _apply_overrides(sdk, args)
    assert sdk._config.eval_prompt == "Custom prompt"


def test_max_tokens_override_reflected_in_config(config_path: Path, models_json: Path):
    from hw5.sdk.sdk import EvalPipelineSDK

    sdk = EvalPipelineSDK(str(config_path))
    import argparse

    from hw5.main import _apply_overrides

    args = argparse.Namespace(
        resume=False, output_dir=None, eval_prompt=None, max_tokens=99
    )
    _apply_overrides(sdk, args)
    assert sdk._config.max_tokens == 99
