"""T711–T730: Edge case tests covering error paths and boundary conditions."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from hw5.services.cell_persistence import load_existing_results, save_result
from hw5.services.cell_result import CellResult
from hw5.services.metrics_buffer import MetricsBuffer, VRAMSpikeEvent
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.model_registry import ModelRegistry, RegistryError
from hw5.services.plotter import Plotter
from hw5.services.report import ReportGenerator
from hw5.services.runner_factory import RunnerFactory
from hw5.services.runner_protocol import InferenceResult
from hw5.services.summary import SummaryGenerator
from hw5.shared.config import Config, ConfigError
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

# ── helpers ───────────────────────────────────────────────────────────────────


def _snap(ram: float = 100.0) -> MetricsSnapshot:
    return MetricsSnapshot(
        samples=[], spike_events=[], peak_ram_mb=ram,
        peak_vram_mb=0.0, peak_swap_mb=0.0, avg_cpu_pct=10.0, total_disk_read_mb=0.0,
    )


def _ir(fw: str = "ollama") -> InferenceResult:
    return InferenceResult(
        output_text="ok", tokens_generated=5, total_time_s=1.0,
        first_token_latency_s=0.0, framework=fw, model_id="m", quant="Q4",
    )


def _cell(cell_id: str, failed: bool = False) -> CellResult:
    return CellResult(
        cell_id=cell_id, inference=_ir(), metrics=_snap(),
        started_at=0.0, finished_at=1.0, failed=failed,
    )


# ── T711/T721: Plotter with all-failed results ────────────────────────────────


def test_plotter_with_all_failed_results_empty_df(config):
    results = [_cell("a__ollama__Q4", failed=True), _cell("b__airllm__Q8", failed=True)]
    p = Plotter(results, config)
    assert p._get_df().empty


def test_plotter_all_failed_plots_do_not_crash(config):
    from matplotlib.figure import Figure
    results = [_cell("a__ollama__Q4", failed=True)]
    p = Plotter(results, config)
    for fig in (p.heatmap(), p.ram_timeline(), p.vram_bar_chart(), p.tradeoff_scatter()):
        assert isinstance(fig, Figure)


# ── T712: monitor handles 0 samples ──────────────────────────────────────────


def test_metrics_snapshot_from_empty_buffer():
    buf = MetricsBuffer()
    snap = MetricsSnapshot.from_buffer(buf)
    assert snap.peak_ram_mb == 0.0
    assert snap.avg_cpu_pct == 0.0
    assert snap.samples == []


# ── T713: empty model list raises RegistryError ───────────────────────────────


def test_registry_raises_on_empty_models_json(tmp_path: Path):
    p = tmp_path / "empty.json"
    p.write_text('{"models": []}')
    gk = ApiGatekeeper(rate=10.0, burst=5)
    reg = ModelRegistry(gk)
    with pytest.raises(RegistryError):
        reg.load_config(str(p))


# ── T714: Config with missing required field raises ConfigError ───────────────


def test_config_raises_on_missing_required_field(tmp_path: Path):
    bad = {"frameworks": ["ollama"]}  # missing eval_prompt, max_tokens, etc.
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(ConfigError):
        Config.load(str(p))


# ── T715: ApiGatekeeper with rate=0 raises ValueError ────────────────────────


def test_gatekeeper_raises_on_zero_rate():
    with pytest.raises(ValueError, match="rate must be > 0"):
        ApiGatekeeper(rate=0.0)


# ── T716: QuantizationConfig with unsupported label raises ValueError ─────────


def test_quant_config_raises_on_unknown_label():
    with pytest.raises(ValueError):
        QuantizationConfig.from_label("Q16")


def test_quant_config_validate_raises_on_unsupported_bits():
    qc = QuantizationConfig(bits=16, label="Q16")
    with pytest.raises(ValueError):
        qc.validate()


# ── T717/T718: Runner.infer without load raises RunnerError ──────────────────


def test_ollama_runner_infer_without_load_raises(config, mock_gatekeeper):
    from hw5.services.ollama_runner import OllamaRunner, RunnerError
    with patch("hw5.services.ollama_runner._ollama"):
        runner = OllamaRunner(config, mock_gatekeeper)
        with pytest.raises(RunnerError):
            runner.infer("hello")


def test_airllm_runner_infer_without_load_raises(config, mock_gatekeeper):
    from hw5.services.airllm_runner import AirLLMRunner
    from hw5.services.airllm_types import RunnerError
    runner = AirLLMRunner(config, mock_gatekeeper)
    with pytest.raises(RunnerError):
        runner.infer("hello")


# ── T719: monitor.stop() called twice is idempotent ──────────────────────────


def test_monitor_stop_twice_is_idempotent(config):
    from hw5.services.monitor import SystemMonitor
    mon = SystemMonitor(config)
    snap1 = mon.stop()
    snap2 = mon.stop()
    assert isinstance(snap1, MetricsSnapshot)
    assert isinstance(snap2, MetricsSnapshot)


# ── T720: save_result raises on non-writable dir ─────────────────────────────


def test_save_result_raises_on_permission_error():
    cr = _cell("m__fw__Q4")
    with patch("hw5.services.cell_persistence.Path.mkdir", side_effect=PermissionError):
        with pytest.raises((PermissionError, OSError)):
            save_result(cr, "/bad/path")


# ── T722: ReportGenerator with no plot files raises no exception ──────────────


def test_report_generator_no_plots_no_exception():
    gen = ReportGenerator({"heatmap": "ok"}, {}, [_cell("a__ollama__Q4")])
    html = gen.to_html()
    assert "<!DOCTYPE html>" in html


# ── T723: SummaryGenerator with single cell ───────────────────────────────────


def test_summary_generator_single_cell_produces_valid_output():
    results = [_cell("model_a__ollama__Q4")]
    sg = SummaryGenerator(results)
    all_summaries = sg.generate_all()
    assert all(isinstance(v, str) and len(v) > 0 for v in all_summaries.values())


# ── T724: corrupt JSON in load_existing_results is skipped ───────────────────


def test_load_existing_results_skips_corrupt_json(tmp_path: Path):
    (tmp_path / "cell_bad.json").write_text("{not valid json}")
    good = _cell("good__ollama__Q4")
    save_result(good, str(tmp_path))
    loaded = load_existing_results(str(tmp_path))
    assert "good__ollama__Q4" in loaded
    assert "bad" not in loaded


# ── T725: Config.get returns default for missing key ─────────────────────────


def test_config_get_returns_default_for_missing_key(config):
    assert config.get("nonexistent_key", "default_val") == "default_val"


# ── T726: ModelRegistry.validate detects HOOK placeholder ────────────────────


def test_registry_validate_detects_hook_placeholder(tmp_path: Path):
    data = {"models": [{
        "name": "m", "hf_repo_id": "<HOOK:hf_repo_id>", "ollama_tag": "m:7b",
        "local_cache": "/tmp/m", "size_class": "large", "param_count_b": 7.0,
        "ollama_compatible": True, "airllm_compatible": True, "description": "test",
        "quant_ollama_tags": {}, "quant_airllm_params": {},
    }]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(data))
    gk = ApiGatekeeper(rate=10.0, burst=5)
    reg = ModelRegistry(gk)
    with pytest.raises(RegistryError, match="HOOK"):
        reg.load_config(str(p))


# ── T727: RunnerFactory with empty string raises ValueError ──────────────────


def test_runner_factory_empty_string_raises_value_error(config, mock_gatekeeper):
    with pytest.raises(ValueError):
        RunnerFactory.create("", config, mock_gatekeeper)


# ── T728: VRAMSpikeEvent roundtrip ────────────────────────────────────────────


def test_vram_spike_event_roundtrip():
    ev = VRAMSpikeEvent(timestamp=1.5, prev_vram_mb=100.0, curr_vram_mb=700.0, delta_mb=600.0)
    restored = VRAMSpikeEvent.from_dict(ev.to_dict())
    assert restored.delta_mb == pytest.approx(600.0)
    assert restored.is_significant(500.0) is True
    assert restored.is_significant(700.0) is False


# ── T729: MetricsBuffer thread safety under 100 concurrent writes ─────────────


def test_metrics_buffer_thread_safety_100_writers():
    buf = MetricsBuffer()
    errors: list[Exception] = []

    def writer(n: int) -> None:
        try:
            for _ in range(n):
                buf.append({"v": 1})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer, args=(10,)) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(buf) == 1000


# ── T730: CellResult.from_dict handles missing optional fields ────────────────


def test_cell_result_from_dict_handles_missing_optional_fields():
    minimal = {
        "cell_id": "m__fw__Q4",
        "inference": {
            "output_text": "", "tokens_generated": 0, "total_time_s": 0.0,
            "first_token_latency_s": 0.0, "framework": "ollama",
            "model_id": "m", "quant": "Q4",
        },
        "metrics": {
            "samples": [], "spike_events": [], "peak_ram_mb": 0.0,
            "peak_vram_mb": 0.0, "peak_swap_mb": 0.0, "avg_cpu_pct": 0.0,
            "total_disk_read_mb": 0.0,
        },
        "started_at": 0.0,
        "finished_at": 1.0,
    }
    cr = CellResult.from_dict(minimal)
    assert cr.cpu_only is False
    assert cr.failed is False
    assert cr.error_message == ""
