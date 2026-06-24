"""T605–T608: Unit tests for SummaryGenerator."""

from __future__ import annotations

from hw5.services.cell_result import CellResult
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.runner_protocol import InferenceResult
from hw5.services.summary import SummaryGenerator

# ── helpers ───────────────────────────────────────────────────────────────────


def _snap(
    ram: float = 400.0, vram: float = 0.0, swap: float = 0.0, spikes: int = 0
) -> MetricsSnapshot:
    return MetricsSnapshot(
        samples=[],
        spike_events=[{"delta_mb": 600.0}] * spikes,
        peak_ram_mb=ram,
        peak_vram_mb=vram,
        peak_swap_mb=swap,
        avg_cpu_pct=30.0,
        total_disk_read_mb=0.0,
    )


def _cell(
    cell_id: str,
    tps: float,
    ram: float = 300.0,
    vram: float = 0.0,
    swap: float = 0.0,
    failed: bool = False,
    spikes: int = 0,
) -> CellResult:
    p = cell_id.split("__")
    ir = InferenceResult(
        output_text="ok",
        tokens_generated=int(tps),
        total_time_s=1.0,
        first_token_latency_s=0.0,
        framework=p[1],
        model_id="test",
        quant=p[2],
    )
    return CellResult(
        cell_id=cell_id,
        inference=ir,
        metrics=_snap(ram=ram, vram=vram, swap=swap, spikes=spikes),
        started_at=0.0,
        finished_at=1.0,
        failed=failed,
    )


RESULTS = [
    _cell("model_a__ollama__Q4", tps=20.0, ram=600.0),
    _cell("model_a__airllm__Q4", tps=15.0, ram=200.0),
    _cell("model_b__ollama__Q8", tps=18.0, ram=500.0, swap=50.0),
    _cell("model_b__airllm__Q8", tps=5.0, ram=150.0, vram=0.0, spikes=2),
    _cell("model_b__ollama__Q2", tps=0.0, failed=True),
]


# ── T605: summarize_heatmap ────────────────────────────────────────────────────


def test_summarize_heatmap_returns_non_empty_string():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_heatmap()
    assert isinstance(s, str) and len(s) > 0


def test_summarize_heatmap_mentions_best_framework():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_heatmap()
    assert "ollama" in s or "airllm" in s


def test_summarize_heatmap_empty_results():
    sg = SummaryGenerator([])
    assert "No successful" in sg.summarize_heatmap()


# ── T606: summarize_timeline identifies highest peak RAM ─────────────────────


def test_summarize_timeline_identifies_highest_peak_ram():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_timeline()
    assert "600" in s or "600.0" in s


def test_summarize_timeline_mentions_swap_when_triggered():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_timeline()
    assert "swap" in s.lower() or "Swap" in s


def test_summarize_timeline_no_swap_message_when_no_swap():
    no_swap = [_cell("model_a__ollama__Q4", tps=10.0, ram=300.0)]
    sg = SummaryGenerator(no_swap)
    s = sg.summarize_timeline()
    assert "No swap" in s


# ── T607: summarize_vram mentions AirLLM ─────────────────────────────────────


def test_summarize_vram_mentions_airllm_framework():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_vram()
    assert "AirLLM" in s


def test_summarize_vram_reports_spike_count():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_vram()
    assert "2" in s or "spike" in s.lower()


def test_summarize_tradeoff_returns_non_empty_string():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_tradeoff()
    assert isinstance(s, str) and len(s) > 0


def test_summarize_tradeoff_mentions_a_quant_level():
    sg = SummaryGenerator(RESULTS)
    s = sg.summarize_tradeoff()
    assert any(q in s for q in ("Q4", "Q8", "Q2"))


# ── T608: generate_all returns dict with all four keys ────────────────────────


def test_generate_all_returns_dict_with_four_keys():
    sg = SummaryGenerator(RESULTS)
    result = sg.generate_all()
    assert set(result.keys()) == {
        "heatmap",
        "ram_timeline",
        "vram_bar",
        "tradeoff_scatter",
    }


def test_generate_all_values_are_non_empty_strings():
    sg = SummaryGenerator(RESULTS)
    for key, val in sg.generate_all().items():
        assert isinstance(val, str) and len(val) > 0, f"empty summary for {key}"
