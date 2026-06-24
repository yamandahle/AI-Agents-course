"""T181–T260: Tests for MetricsBuffer, VRAMSpikeEvent, MetricsSnapshot, SystemMonitor."""

from __future__ import annotations

import threading
import time

import pytest

from hw5.services.metrics_buffer import MetricsBuffer, VRAMSpikeEvent
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.monitor import SystemMonitor

# ── helpers ───────────────────────────────────────────────────────────────────


def _sample(
    ts: float = 0.0,
    cpu: float = 10.0,
    ram: float = 1000.0,
    swap: float = 50.0,
    vram: float = 0.0,
    disk_read: float = 100.0,
    disk_write: float = 50.0,
    page_faults: int = 0,
    cpu_cores: list[float] | None = None,
) -> dict:
    return {
        "ts": ts,
        "cpu": cpu,
        "ram": ram,
        "swap": swap,
        "vram": vram,
        "disk_read": disk_read,
        "disk_write": disk_write,
        "page_faults": page_faults,
        "cpu_cores": cpu_cores or [cpu],
    }


def _fast_config(config):
    """Return config with 50 ms monitor interval for speed in tests."""
    config.monitor_interval_s = 0.05
    return config


# ── T240: VRAMSpikeEvent ──────────────────────────────────────────────────────


def test_spike_event_is_significant_above_threshold():
    event = VRAMSpikeEvent(
        timestamp=1.0, prev_vram_mb=100.0, curr_vram_mb=700.0, delta_mb=600.0
    )
    assert event.is_significant(500.0) is True


def test_spike_event_not_significant_below_threshold():
    event = VRAMSpikeEvent(
        timestamp=1.0, prev_vram_mb=100.0, curr_vram_mb=200.0, delta_mb=100.0
    )
    assert event.is_significant(500.0) is False


def test_spike_event_to_dict_from_dict_roundtrip():
    event = VRAMSpikeEvent(
        timestamp=2.5, prev_vram_mb=50.0, curr_vram_mb=600.0, delta_mb=550.0
    )
    restored = VRAMSpikeEvent.from_dict(event.to_dict())
    assert restored.delta_mb == pytest.approx(550.0)
    assert restored.timestamp == pytest.approx(2.5)


# ── T237: MetricsBuffer ───────────────────────────────────────────────────────


def test_metrics_buffer_thread_safe():
    buf = MetricsBuffer()
    threads = [
        threading.Thread(target=buf.append, args=({"i": i},)) for i in range(100)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(buf) == 100


def test_metrics_buffer_clear_empties_buffer():
    buf = MetricsBuffer()
    buf.append({"x": 1})
    buf.clear()
    assert len(buf) == 0


def test_metrics_buffer_to_list_is_copy():
    buf = MetricsBuffer()
    buf.append({"x": 1})
    lst = buf.to_list()
    lst.append({"x": 2})
    assert len(buf) == 1  # original unaffected


# ── T236: MetricsSnapshot.from_buffer ────────────────────────────────────────


def test_from_buffer_empty_returns_zeros():
    buf = MetricsBuffer()
    snap = MetricsSnapshot.from_buffer(buf)
    assert snap.peak_ram_mb == pytest.approx(0.0)
    assert snap.avg_cpu_pct == pytest.approx(0.0)
    assert snap.samples == []


def test_from_buffer_computes_peaks():
    buf = MetricsBuffer()
    buf.append(_sample(ts=0.0, cpu=10.0, ram=1000.0, swap=100.0, disk_read=0.0))
    buf.append(_sample(ts=0.5, cpu=50.0, ram=2000.0, swap=200.0, disk_read=100.0))
    snap = MetricsSnapshot.from_buffer(buf)
    assert snap.peak_ram_mb == pytest.approx(2000.0)
    assert snap.peak_swap_mb == pytest.approx(200.0)
    assert snap.avg_cpu_pct == pytest.approx(30.0)
    assert snap.total_disk_read_mb == pytest.approx(100.0)


def test_from_buffer_spike_events_included():
    buf = MetricsBuffer()
    buf.append(_sample())
    spike_buf = MetricsBuffer()
    spike_buf.append(
        {
            "timestamp": 1.0,
            "delta_mb": 600.0,
            "prev_vram_mb": 0.0,
            "curr_vram_mb": 600.0,
        }
    )
    snap = MetricsSnapshot.from_buffer(buf, spike_buf)
    assert len(snap.spike_events) == 1
    assert snap.spike_events[0]["delta_mb"] == pytest.approx(600.0)


def test_from_buffer_page_faults_delta():
    buf = MetricsBuffer()
    buf.append(_sample(page_faults=100))
    buf.append(_sample(page_faults=150))
    snap = MetricsSnapshot.from_buffer(buf)
    assert snap.page_faults_delta == 50


# ── T239: to_dict / from_dict roundtrip ──────────────────────────────────────


def test_metrics_snapshot_to_dict_from_dict_roundtrip():
    buf = MetricsBuffer()
    buf.append(_sample(ram=3000.0, cpu=25.0))
    snap = MetricsSnapshot.from_buffer(buf)
    restored = MetricsSnapshot.from_dict(snap.to_dict())
    assert restored.peak_ram_mb == pytest.approx(3000.0)
    assert restored.avg_cpu_pct == pytest.approx(25.0)


# ── T230–T234: SystemMonitor ──────────────────────────────────────────────────


def test_monitor_starts_and_stops_cleanly(config):
    mon = SystemMonitor(_fast_config(config))
    mon.start()
    time.sleep(0.15)
    snap = mon.stop()
    assert isinstance(snap, MetricsSnapshot)


def test_monitor_collects_samples(config):
    mon = SystemMonitor(_fast_config(config))
    mon.start()
    time.sleep(0.3)
    snap = mon.stop()
    assert len(snap.samples) > 0


def test_monitor_snapshot_avg_cpu_is_valid_float(config):
    mon = SystemMonitor(_fast_config(config))
    mon.start()
    time.sleep(0.2)
    snap = mon.stop()
    assert isinstance(snap.avg_cpu_pct, float)
    assert 0.0 <= snap.avg_cpu_pct <= 100.0


def test_monitor_stop_terminates_within_two_seconds(config):
    mon = SystemMonitor(_fast_config(config))
    mon.start()
    t0 = time.monotonic()
    mon.stop()
    assert time.monotonic() - t0 < 2.0


# ── T233/T234: spike detection ────────────────────────────────────────────────


def test_spike_detected_above_threshold(config):
    mon = SystemMonitor(config)
    mon._nvml_available = False
    prev = _sample(vram=100.0, ts=0.0)
    curr = _sample(vram=700.0, ts=0.5)
    result = mon._detect_spike(prev, curr)
    assert result is True
    assert len(mon._spike_buffer) == 1


def test_spike_not_detected_below_threshold(config):
    mon = SystemMonitor(config)
    mon._nvml_available = False
    prev = _sample(vram=100.0, ts=0.0)
    curr = _sample(vram=200.0, ts=0.5)
    result = mon._detect_spike(prev, curr)
    assert result is False
    assert len(mon._spike_buffer) == 0


# ── T235: _sample_vram without GPU ───────────────────────────────────────────


def test_sample_vram_returns_zero_without_gpu(config):
    mon = SystemMonitor(config)
    mon._nvml_available = False
    assert mon._sample_vram() == pytest.approx(0.0)


# ── T244: performance — 1000 samples ─────────────────────────────────────────


def test_metrics_buffer_handles_1000_samples():
    buf = MetricsBuffer()
    for i in range(1000):
        buf.append(_sample(ts=float(i), ram=float(1000 + i)))
    assert len(buf) == 1000
    snap = MetricsSnapshot.from_buffer(buf)
    assert snap.peak_ram_mb == pytest.approx(1999.0)


# ── T226–T228: Rich display ───────────────────────────────────────────────────


def test_get_live_table_with_samples_returns_table(config):
    from rich.table import Table

    mon = SystemMonitor(config)
    mon._buffer.append(_sample(cpu=42.0, ram=2048.0, swap=100.0, vram=0.0))
    table = mon.get_live_table()
    assert isinstance(table, Table)


def test_get_live_table_empty_returns_table(config):
    from rich.table import Table

    mon = SystemMonitor(config)
    table = mon.get_live_table()
    assert isinstance(table, Table)


def test_print_latest_does_not_raise(config, capsys):
    mon = SystemMonitor(config)
    mon._buffer.append(_sample(cpu=10.0, ram=1024.0))
    mon.print_latest()
    # Rich prints to its own console — no assertion on stdout needed
