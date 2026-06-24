"""T731–T736: Performance and timing tests."""

from __future__ import annotations

import json
import time
from pathlib import Path

from hw5.services.cell_result import CellResult
from hw5.services.metrics_buffer import MetricsBuffer
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.plotter import Plotter
from hw5.services.report import ReportGenerator
from hw5.services.runner_protocol import InferenceResult
from hw5.services.summary import SummaryGenerator
from hw5.shared.config import Config

# ── helpers ───────────────────────────────────────────────────────────────────


def _snap() -> MetricsSnapshot:
    return MetricsSnapshot(
        samples=[],
        spike_events=[],
        peak_ram_mb=300.0,
        peak_vram_mb=0.0,
        peak_swap_mb=0.0,
        avg_cpu_pct=15.0,
        total_disk_read_mb=0.0,
    )


def _ir(fw: str = "ollama") -> InferenceResult:
    return InferenceResult(
        output_text="hi",
        tokens_generated=10,
        total_time_s=1.0,
        first_token_latency_s=0.1,
        framework=fw,
        model_id="m",
        quant="Q4",
    )


def _cell(n: int) -> CellResult:
    fw = "ollama" if n % 2 == 0 else "airllm"
    q = ("Q4", "Q8", "Q2")[n % 3]
    return CellResult(
        cell_id=f"model_{n % 5}__{fw}__{q}",
        inference=_ir(fw),
        metrics=_snap(),
        started_at=float(n),
        finished_at=float(n + 1),
    )


# ── T731: MetricsBuffer handles 10,000 items ──────────────────────────────────


def test_metrics_buffer_handles_10k_items():
    buf = MetricsBuffer()
    for i in range(10_000):
        buf.append({"cpu": i})
    assert len(buf) == 10_000


# ── T732: Plotter._get_df processes 100 CellResults in <1s ───────────────────


def test_plotter_get_df_100_cells_under_1s(config: Config):
    results = [_cell(i) for i in range(100)]
    p = Plotter(results, config)
    t0 = time.perf_counter()
    df = p._get_df()
    elapsed = time.perf_counter() - t0
    assert len(df) == 100
    assert elapsed < 1.0


# ── T733: SummaryGenerator.generate_all in <100ms ────────────────────────────


def test_summary_generator_generate_all_under_100ms():
    results = [_cell(i) for i in range(12)]
    sg = SummaryGenerator(results)
    t0 = time.perf_counter()
    all_summaries = sg.generate_all()
    elapsed = time.perf_counter() - t0
    assert len(all_summaries) == 4
    assert elapsed < 0.1


# ── T734: ReportGenerator.to_html with embedded images in <5s ────────────────


def test_report_generator_to_html_with_images_under_5s(tmp_path: Path):
    pngs = {}
    for name in ("heatmap", "ram_timeline", "vram_bar", "tradeoff_scatter"):
        p = tmp_path / f"{name}.png"
        p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 1024)
        pngs[f"{name}.png"] = p

    summaries = {k.replace(".png", ""): "summary" for k in pngs}
    results = [_cell(i) for i in range(3)]
    gen = ReportGenerator(summaries, pngs, results)

    t0 = time.perf_counter()
    html = gen.to_html()
    elapsed = time.perf_counter() - t0

    assert "<!DOCTYPE html>" in html
    assert elapsed < 5.0


# ── T735: Config.load parses JSON in <10ms ────────────────────────────────────


def test_config_load_parses_in_under_10ms(tmp_path: Path):
    data = {
        "quantization_levels": ["Q4", "Q8", "Q2"],
        "frameworks": ["ollama", "airllm"],
        "eval_prompt": "prompt",
        "max_tokens": 100,
        "monitor_interval_s": 0.5,
        "vram_spike_threshold_mb": 500.0,
        "results_dir": str(tmp_path / "r"),
        "assets_dir": str(tmp_path / "a"),
    }
    p = tmp_path / "setup.json"
    p.write_text(json.dumps(data))

    t0 = time.perf_counter()
    cfg = Config.load(str(p))
    elapsed = time.perf_counter() - t0

    assert cfg.max_tokens == 100
    assert elapsed < 0.01


# ── T736: ModelRegistry.load_config with 20 models in <100ms ─────────────────


def test_model_registry_loads_20_models_under_100ms(tmp_path: Path):
    from hw5.services.model_registry import ModelRegistry
    from hw5.shared.gatekeeper import ApiGatekeeper

    models = []
    for i in range(20):
        models.append(
            {
                "name": f"model_{i}",
                "hf_repo_id": f"org/model-{i}",
                "ollama_tag": f"model-{i}:7b",
                "local_cache": str(tmp_path / f"cache_{i}"),
                "size_class": "small",
                "param_count_b": 1.5,
                "ollama_compatible": True,
                "airllm_compatible": True,
                "description": f"Model {i}",
                "quant_ollama_tags": {"Q4": f"model-{i}:7b-q4_K_M"},
                "quant_airllm_params": {"Q4": "4bit"},
            }
        )
    p = tmp_path / "models.json"
    p.write_text(json.dumps({"models": models}))

    gk = ApiGatekeeper(rate=100.0, burst=10)
    reg = ModelRegistry(gk)

    t0 = time.perf_counter()
    reg.load_config(str(p))
    elapsed = time.perf_counter() - t0

    assert reg.count == 20
    assert elapsed < 0.1
