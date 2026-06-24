"""SystemMonitor — daemon thread that samples OS metrics while inference runs."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Any

import psutil
from rich.console import Console
from rich.table import Table

from hw5.services.metrics_buffer import MetricsBuffer, VRAMSpikeEvent
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.shared.config import Config

log = logging.getLogger(__name__)

try:
    import pynvml as _pynvml

    _PYNVML_AVAILABLE = True
except ImportError:
    _pynvml = None  # type: ignore[assignment]
    _PYNVML_AVAILABLE = False


class SystemMonitor:
    """Samples CPU, RAM, swap, VRAM, and disk I/O on a daemon thread."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._buffer = MetricsBuffer()
        self._spike_buffer = MetricsBuffer()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._start_ts: float = 0.0
        self._nvml_handle: Any = None
        self._nvml_available = self._init_nvml()

    def start(self) -> None:
        self._start_ts = time.perf_counter()
        self._buffer.clear()
        self._spike_buffer.clear()
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="SystemMonitor"
        )
        self._thread.start()

    def stop(self) -> MetricsSnapshot:
        """Stop sampling and return aggregated MetricsSnapshot."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        self._shutdown_nvml()
        return MetricsSnapshot.from_buffer(self._buffer, self._spike_buffer)

    def _run(self) -> None:
        prev: dict[str, Any] | None = None
        while not self._stop_event.is_set():
            sample = self._sample()
            self._buffer.append(sample)
            if prev is not None:
                self._detect_spike(prev, sample)
            prev = sample
            self._stop_event.wait(self._config.monitor_interval_s)

    def _sample(self) -> dict[str, Any]:
        io = psutil.disk_io_counters()
        return {
            "ts": time.perf_counter() - self._start_ts,
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().used / 1e6,
            "swap": psutil.swap_memory().used / 1e6,
            "vram": self._sample_vram(),
            "disk_read": io.read_bytes / 1e6 if io else 0.0,
            "disk_write": io.write_bytes / 1e6 if io else 0.0,
            "page_faults": self._sample_page_faults(),
            "cpu_cores": psutil.cpu_percent(percpu=True),
        }

    def _sample_vram(self) -> float:
        if not self._nvml_available or self._nvml_handle is None:
            return 0.0
        try:
            info = _pynvml.nvmlDeviceGetMemoryInfo(self._nvml_handle)
            return info.used / 1e6
        except Exception:
            return 0.0

    def _sample_page_faults(self) -> int:
        try:
            fields = Path("/proc/self/stat").read_text().split()
            return int(fields[9]) + int(fields[11])  # minflt + majflt
        except Exception:
            return 0

    def _detect_spike(self, prev: dict[str, Any], curr: dict[str, Any]) -> bool:
        delta = curr["vram"] - prev["vram"]
        if delta > self._config.vram_spike_threshold_mb:
            event = VRAMSpikeEvent(
                timestamp=curr["ts"],
                prev_vram_mb=prev["vram"],
                curr_vram_mb=curr["vram"],
                delta_mb=delta,
            )
            self._spike_buffer.append(event.to_dict())
            log.info("VRAM spike: +%.1f MB at t=%.2fs", delta, curr["ts"])
            return True
        return False

    def _init_nvml(self) -> bool:
        if not _PYNVML_AVAILABLE:
            return False
        try:
            _pynvml.nvmlInit()
            self._nvml_handle = _pynvml.nvmlDeviceGetHandleByIndex(0)
            return True
        except Exception:
            log.debug("No NVIDIA GPU — VRAM monitoring disabled")
            return False

    def _shutdown_nvml(self) -> None:
        if self._nvml_available and _PYNVML_AVAILABLE:
            try:
                _pynvml.nvmlShutdown()
            except Exception:
                pass

    def get_live_table(self) -> Table:
        """Return a Rich Table showing the latest monitoring sample."""
        table = Table(title="System Monitor", show_header=True)
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        samples = self._buffer.to_list()
        if samples:
            s = samples[-1]
            table.add_row("CPU %", f"{s.get('cpu', 0.0):.1f}")
            table.add_row("RAM MB", f"{s.get('ram', 0.0):.1f}")
            table.add_row("Swap MB", f"{s.get('swap', 0.0):.1f}")
            table.add_row("VRAM MB", f"{s.get('vram', 0.0):.1f}")
            table.add_row("Samples", str(len(samples)))
        return table

    def print_latest(self, n: int = 5) -> None:
        Console().print(self.get_live_table())
