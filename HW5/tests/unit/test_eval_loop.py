"""T486–T518: Unit tests for CellResult, cell_persistence, and EvaluationLoop."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hw5.services.cell_persistence import load_existing_results, save_result
from hw5.services.cell_result import CellResult
from hw5.services.eval_loop import EvaluationLoop
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.model_registry import ModelRegistry
from hw5.services.runner_protocol import InferenceResult
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

# ── helpers ───────────────────────────────────────────────────────────────────


def _empty_metrics() -> MetricsSnapshot:
    return MetricsSnapshot(
        samples=[],
        spike_events=[],
        peak_ram_mb=0.0,
        peak_vram_mb=0.0,
        peak_swap_mb=0.0,
        avg_cpu_pct=0.0,
        total_disk_read_mb=0.0,
    )


def _mock_infer(framework: str = "ollama", quant: str = "Q4") -> InferenceResult:
    return InferenceResult(
        output_text="hello",
        tokens_generated=5,
        total_time_s=1.0,
        first_token_latency_s=0.1,
        framework=framework,
        model_id="test-model",
        quant=quant,
    )


def _make_cell_result(cell_id: str = "model_a__ollama__Q4") -> CellResult:
    return CellResult(
        cell_id=cell_id,
        inference=_mock_infer(),
        metrics=_empty_metrics(),
        started_at=1000.0,
        finished_at=1002.0,
    )


@pytest.fixture
def registry(models_json: Path, mock_gatekeeper: MagicMock) -> ModelRegistry:
    reg = ModelRegistry(mock_gatekeeper)
    reg.load_config(str(models_json))
    return reg


def _loop(config, registry) -> EvaluationLoop:
    return EvaluationLoop(config, registry, ApiGatekeeper(rate=1000.0, burst=100))


def _mock_runner(framework: str = "ollama") -> MagicMock:
    r = MagicMock()
    r.infer.return_value = _mock_infer(framework)
    return r


def _mock_monitor() -> MagicMock:
    m = MagicMock()
    m.stop.return_value = _empty_metrics()
    return m


# ── T500: CellResult to_dict / from_dict roundtrip ───────────────────────────


def test_cell_result_to_dict_from_dict_roundtrip():
    cr = _make_cell_result("model_a__ollama__Q4")
    restored = CellResult.from_dict(cr.to_dict())
    assert restored.cell_id == "model_a__ollama__Q4"
    assert restored.failed is False
    assert restored.duration_s == pytest.approx(2.0)


# ── T497: duration_s property ────────────────────────────────────────────────


def test_cell_result_duration_s_computed_correctly():
    cr = _make_cell_result()
    assert cr.duration_s == pytest.approx(2.0)


# ── T491/T503: save_result ────────────────────────────────────────────────────


def test_save_result_creates_json_with_correct_filename(tmp_path: Path):
    cr = _make_cell_result("model_a__ollama__Q4")
    path = save_result(cr, str(tmp_path / "results"))
    assert path.name == "cell_model_a__ollama__Q4.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["cell_id"] == "model_a__ollama__Q4"


def test_save_result_returns_existing_path_without_overwriting(tmp_path: Path):
    cr = _make_cell_result("m__fw__Q4")
    rdir = str(tmp_path / "r")
    path1 = save_result(cr, rdir)
    original_mtime = path1.stat().st_mtime
    path2 = save_result(cr, rdir)
    assert path1 == path2
    assert path2.stat().st_mtime == original_mtime


# ── T492: load_existing_results ───────────────────────────────────────────────


def test_load_existing_results_returns_cell_result(tmp_path: Path):
    cr = _make_cell_result("model_a__airllm__Q8")
    save_result(cr, str(tmp_path))
    loaded = load_existing_results(str(tmp_path))
    assert "model_a__airllm__Q8" in loaded
    assert loaded["model_a__airllm__Q8"].cell_id == "model_a__airllm__Q8"


def test_load_existing_results_returns_empty_for_missing_dir(tmp_path: Path):
    result = load_existing_results(str(tmp_path / "nonexistent"))
    assert result == {}


# ── T486/T487: iter_cells ─────────────────────────────────────────────────────


def test_iter_cells_yields_all_combinations(config, registry):
    cells = list(_loop(config, registry).iter_cells())
    n_models = registry.count
    n_frameworks = len(config.frameworks)
    n_quants = len(config.quantization_levels)
    assert len(cells) == n_models * n_frameworks * n_quants


def test_iter_cells_tuples_have_correct_types(config, registry):
    from hw5.services.model_entry import ModelEntry

    for entry, fw, quant in _loop(config, registry).iter_cells():
        assert isinstance(entry, ModelEntry)
        assert fw in ("ollama", "airllm")
        assert isinstance(quant, QuantizationConfig)


# ── T496: cell_id format ─────────────────────────────────────────────────────


@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_cell_id_format(mock_factory, mock_mon_cls, config, registry):
    mock_factory.create.return_value = _mock_runner()
    mock_mon_cls.return_value = _mock_monitor()
    loop = _loop(config, registry)
    entry = registry.get_model("model_a")
    quant = QuantizationConfig.from_label("Q4")
    result = loop.run_cell(entry, "ollama", quant)
    assert result.cell_id == "model_a__ollama__Q4"


# ── T488: run_cell call order ─────────────────────────────────────────────────


@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_cell_calls_load_infer_unload_in_order(
    mock_factory, mock_mon_cls, config, registry
):
    log: list[str] = []
    runner = MagicMock()
    runner.load.side_effect = lambda *a, **kw: log.append("load")
    runner.infer.side_effect = lambda *a, **kw: (log.append("infer"), _mock_infer())[1]
    runner.unload.side_effect = lambda: log.append("unload")
    mock_factory.create.return_value = runner
    mon = MagicMock()
    mon.stop.return_value = _empty_metrics()
    mock_mon_cls.return_value = mon
    _loop(config, registry).run_cell(
        registry.get_model("model_a"), "ollama", QuantizationConfig.from_label("Q4")
    )
    assert log == ["load", "infer", "unload"]


# ── T489: monitor.start before load ──────────────────────────────────────────


@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_cell_starts_monitor_before_load(
    mock_factory, mock_mon_cls, config, registry
):
    log: list[str] = []
    runner = MagicMock()
    runner.load.side_effect = lambda *a, **kw: log.append("load")
    runner.infer.return_value = _mock_infer()
    mock_factory.create.return_value = runner
    mon = MagicMock()
    mon.start.side_effect = lambda: log.append("start")
    mon.stop.return_value = _empty_metrics()
    mock_mon_cls.return_value = mon
    _loop(config, registry).run_cell(
        registry.get_model("model_b"), "ollama", QuantizationConfig.from_label("Q4")
    )
    assert log.index("start") < log.index("load")


# ── T490/T499: monitor.stop in finally ───────────────────────────────────────


@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_cell_stops_monitor_even_on_failure(
    mock_factory, mock_mon_cls, config, registry
):
    runner = MagicMock()
    runner.load.side_effect = RuntimeError("crash")
    mock_factory.create.return_value = runner
    mon = MagicMock()
    mon.stop.return_value = _empty_metrics()
    mock_mon_cls.return_value = mon
    result = _loop(config, registry).run_cell(
        registry.get_model("model_a"), "ollama", QuantizationConfig.from_label("Q4")
    )
    mon.stop.assert_called_once()
    assert result.failed is True


# ── T494/T495: failure handling ───────────────────────────────────────────────


@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_cell_failure_stored_in_result(
    mock_factory, mock_mon_cls, config, registry
):
    runner = MagicMock()
    runner.load.side_effect = RuntimeError("OOM")
    mock_factory.create.return_value = runner
    mock_mon_cls.return_value = _mock_monitor()
    result = _loop(config, registry).run_cell(
        registry.get_model("model_a"), "ollama", QuantizationConfig.from_label("Q4")
    )
    assert result.failed is True
    assert "OOM" in result.error_message


@patch("hw5.services.eval_loop.Progress")
@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_failure_does_not_stop_remaining_cells(
    mock_factory, mock_mon_cls, mock_prog, config, registry
):
    call_counts: list[int] = [0]

    def flaky_load(*a, **kw):
        call_counts[0] += 1
        if call_counts[0] == 1:
            raise RuntimeError("first cell fails")

    runner = MagicMock()
    runner.load.side_effect = flaky_load
    runner.infer.return_value = _mock_infer()
    mock_factory.create.return_value = runner
    mock_mon_cls.return_value = _mock_monitor()
    mock_prog.return_value.__enter__ = lambda s: MagicMock()
    mock_prog.return_value.__exit__ = lambda *a: None
    loop = _loop(config, registry)
    with patch.object(loop, "run_cell", wraps=loop.run_cell):
        results = loop.run()
    assert len(results) == 12  # all 12 cells attempted


# ── T498: get_successful_results ──────────────────────────────────────────────


def test_get_successful_results_excludes_failed(config, registry):
    good = _make_cell_result("a__ollama__Q4")
    bad = _make_cell_result("b__airllm__Q2")
    bad.failed = True
    loop = _loop(config, registry)
    assert loop.get_successful_results([good, bad]) == [good]


# ── T493: resume skips completed cells ───────────────────────────────────────


@patch("hw5.services.eval_loop.Progress")
@patch("hw5.services.eval_loop.SystemMonitor")
@patch("hw5.services.eval_loop.RunnerFactory")
def test_run_skips_cells_with_existing_results(
    mock_factory, mock_mon_cls, mock_prog, config, registry, tmp_path: Path
):
    # Pre-save all 12 cells as existing results
    config.resume = True
    config.results_dir = str(tmp_path / "results")
    loop = _loop(config, registry)
    for entry, fw, quant in loop.iter_cells():
        cr = _make_cell_result(f"{entry.name}__{fw}__{quant}")
        save_result(cr, config.results_dir)
    mock_prog.return_value.__enter__ = lambda s: MagicMock()
    mock_prog.return_value.__exit__ = lambda *a: None
    results = loop.run()
    mock_factory.create.assert_not_called()
    assert len(results) == 12


# ── T517/T518: filter_cells ───────────────────────────────────────────────────


def test_filter_cells_by_model_excludes_other_model(config, registry):
    cells = _loop(config, registry).filter_cells(models=["model_a"])
    assert all(e.name == "model_a" for e, _, _ in cells)
    assert len(cells) == len(config.frameworks) * len(config.quantization_levels)


def test_filter_cells_by_framework(config, registry):
    cells = _loop(config, registry).filter_cells(frameworks=["ollama"])
    assert all(fw == "ollama" for _, fw, _ in cells)


def test_filter_cells_by_quant(config, registry):
    cells = _loop(config, registry).filter_cells(quants=["Q4"])
    assert all(str(q) == "Q4" for _, _, q in cells)


def test_filter_cells_no_filter_returns_all(config, registry):
    all_cells = list(_loop(config, registry).iter_cells())
    filtered = _loop(config, registry).filter_cells()
    assert len(filtered) == len(all_cells)
