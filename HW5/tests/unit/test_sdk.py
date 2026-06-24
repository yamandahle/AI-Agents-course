"""T651–T659: Unit tests for EvalPipelineSDK — verifies delegation to services."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from hw5.sdk.sdk import EvalPipelineSDK
from hw5.services.cell_result import CellResult
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.runner_protocol import InferenceResult

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


def _ir(framework: str = "ollama") -> InferenceResult:
    return InferenceResult(
        output_text="ok",
        tokens_generated=10,
        total_time_s=1.0,
        first_token_latency_s=0.1,
        framework=framework,
        model_id="m",
        quant="Q4",
    )


def _cell(cell_id: str = "model_a__ollama__Q4") -> CellResult:
    return CellResult(
        cell_id=cell_id,
        inference=_ir(),
        metrics=_snap(),
        started_at=0.0,
        finished_at=1.0,
    )


@pytest.fixture
def sdk(config_path: Path, models_json: Path) -> EvalPipelineSDK:
    return EvalPipelineSDK(str(config_path), str(models_json))


# ── T656: initializes without exception ───────────────────────────────────────


def test_sdk_initializes_without_exception(config_path: Path, models_json: Path):
    sdk = EvalPipelineSDK(str(config_path), str(models_json))
    assert sdk._config is not None
    assert sdk._registry is not None


# ── T653: list_models delegates to registry ────────────────────────────────────


def test_list_models_returns_model_names(sdk: EvalPipelineSDK):
    names = sdk.list_models()
    assert isinstance(names, list)
    assert "model_a" in names
    assert "model_b" in names


# ── T652: run_full_evaluation delegates to EvaluationLoop.run ─────────────────


@patch("hw5.sdk.sdk.EvaluationLoop")
def test_run_full_evaluation_calls_loop_run(MockLoop, sdk: EvalPipelineSDK):
    mock_results = [_cell()]
    MockLoop.return_value.run.return_value = mock_results
    results = sdk.run_full_evaluation()
    MockLoop.return_value.run.assert_called_once()
    assert results == mock_results


# ── T657: run_single_cell calls EvaluationLoop.run_cell ──────────────────────


@patch("hw5.sdk.sdk.EvaluationLoop")
def test_run_single_cell_calls_run_cell(MockLoop, sdk: EvalPipelineSDK):
    expected = _cell("model_a__ollama__Q4")
    MockLoop.return_value.run_cell.return_value = expected
    result = sdk.run_single_cell("model_a", "ollama", "Q4")
    MockLoop.return_value.run_cell.assert_called_once()
    assert result == expected


# ── T658: get_results loads JSONs from results dir ────────────────────────────


def test_get_results_from_results_dir(sdk: EvalPipelineSDK, tmp_path: Path):
    from hw5.services.cell_persistence import save_result

    cr = _cell("model_a__airllm__Q8")
    rdir = str(tmp_path / "r")
    save_result(cr, rdir)
    results = sdk.get_results(rdir)
    assert len(results) == 1
    assert results[0].cell_id == "model_a__airllm__Q8"


def test_get_results_returns_empty_list_for_missing_dir(
    sdk: EvalPipelineSDK, tmp_path: Path
):
    results = sdk.get_results(str(tmp_path / "nonexistent"))
    assert results == []


# ── T654: generate_plots calls Plotter.save_all ───────────────────────────────


@patch("hw5.sdk.sdk.Plotter")
def test_generate_plots_calls_save_all(MockPlotter, sdk: EvalPipelineSDK):
    fake_paths = [Path("a.png"), Path("a.svg")]
    MockPlotter.return_value.save_all.return_value = fake_paths
    paths = sdk.generate_plots([_cell()])
    MockPlotter.return_value.save_all.assert_called_once()
    assert paths == fake_paths


# ── T655: generate_report calls ReportGenerator ───────────────────────────────


@patch("hw5.sdk.sdk.ReportGenerator")
@patch("hw5.sdk.sdk.SummaryGenerator")
def test_generate_report_creates_report(
    MockSumm, MockReport, sdk: EvalPipelineSDK, tmp_path: Path
):
    sdk._config.assets_dir = str(tmp_path / "assets")
    MockSumm.return_value.generate_all.return_value = {"heatmap": "x"}
    MockReport.return_value.save.return_value = tmp_path / "report.html"
    path = sdk.generate_report([_cell()])
    MockReport.return_value.save.assert_called_once()
    assert path == tmp_path / "report.html"


# ── generate_summaries delegates to SummaryGenerator ─────────────────────────


@patch("hw5.sdk.sdk.SummaryGenerator")
def test_generate_summaries_delegates(MockSumm, sdk: EvalPipelineSDK):
    expected = {
        "heatmap": "h",
        "ram_timeline": "r",
        "vram_bar": "v",
        "tradeoff_scatter": "t",
    }
    MockSumm.return_value.generate_all.return_value = expected
    result = sdk.generate_summaries([_cell()])
    MockSumm.return_value.generate_all.assert_called_once()
    assert result == expected
