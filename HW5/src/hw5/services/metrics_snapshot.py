"""MetricsSnapshot — aggregate statistics computed from a MetricsBuffer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hw5.services.metrics_buffer import MetricsBuffer


def _core_peaks(samples: list[dict[str, Any]]) -> list[float]:
    """Return the per-core peak CPU% across all samples."""
    if not samples:
        return []
    core_lists = [s.get("cpu_cores", []) for s in samples]
    n_cores = max((len(c) for c in core_lists), default=0)
    peaks: list[float] = []
    for i in range(n_cores):
        peak = max((c[i] for c in core_lists if i < len(c)), default=0.0)
        peaks.append(peak)
    return peaks


@dataclass
class MetricsSnapshot:
    """Immutable aggregate view of a monitoring session."""

    samples: list[dict[str, Any]]
    spike_events: list[dict[str, Any]]
    peak_ram_mb: float
    peak_vram_mb: float
    peak_swap_mb: float
    avg_cpu_pct: float
    total_disk_read_mb: float
    peak_disk_write_mb: float = 0.0
    page_faults_delta: int = 0
    cpu_core_peaks: list[float] = field(default_factory=list)

    @classmethod
    def from_buffer(
        cls,
        buffer: MetricsBuffer,
        spike_buffer: MetricsBuffer | None = None,
    ) -> MetricsSnapshot:
        """Compute aggregate metrics from a MetricsBuffer snapshot."""
        samples = buffer.to_list()
        spikes = spike_buffer.to_list() if spike_buffer is not None else []

        if not samples:
            return cls(
                samples=[],
                spike_events=spikes,
                peak_ram_mb=0.0,
                peak_vram_mb=0.0,
                peak_swap_mb=0.0,
                avg_cpu_pct=0.0,
                total_disk_read_mb=0.0,
                peak_disk_write_mb=0.0,
                page_faults_delta=0,
                cpu_core_peaks=[],
            )

        rams = [s.get("ram", 0.0) for s in samples]
        vrams = [s.get("vram", 0.0) for s in samples]
        swaps = [s.get("swap", 0.0) for s in samples]
        cpus = [s.get("cpu", 0.0) for s in samples]
        disk_reads = [s.get("disk_read", 0.0) for s in samples]
        disk_writes = [s.get("disk_write", 0.0) for s in samples]
        page_faults = [s.get("page_faults", 0) for s in samples]

        return cls(
            samples=samples,
            spike_events=spikes,
            peak_ram_mb=max(rams),
            peak_vram_mb=max(vrams),
            peak_swap_mb=max(swaps),
            avg_cpu_pct=sum(cpus) / len(cpus),
            total_disk_read_mb=max(disk_reads) - min(disk_reads),
            peak_disk_write_mb=max(disk_writes) - min(disk_writes),
            page_faults_delta=max(page_faults) - min(page_faults),
            cpu_core_peaks=_core_peaks(samples),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this snapshot to a plain dictionary."""
        return {
            "samples": self.samples,
            "spike_events": self.spike_events,
            "peak_ram_mb": self.peak_ram_mb,
            "peak_vram_mb": self.peak_vram_mb,
            "peak_swap_mb": self.peak_swap_mb,
            "avg_cpu_pct": self.avg_cpu_pct,
            "total_disk_read_mb": self.total_disk_read_mb,
            "peak_disk_write_mb": self.peak_disk_write_mb,
            "page_faults_delta": self.page_faults_delta,
            "cpu_core_peaks": self.cpu_core_peaks,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MetricsSnapshot:
        """Deserialize a snapshot from a plain dictionary."""
        return cls(
            samples=d.get("samples", []),
            spike_events=d.get("spike_events", []),
            peak_ram_mb=float(d.get("peak_ram_mb", 0.0)),
            peak_vram_mb=float(d.get("peak_vram_mb", 0.0)),
            peak_swap_mb=float(d.get("peak_swap_mb", 0.0)),
            avg_cpu_pct=float(d.get("avg_cpu_pct", 0.0)),
            total_disk_read_mb=float(d.get("total_disk_read_mb", 0.0)),
            peak_disk_write_mb=float(d.get("peak_disk_write_mb", 0.0)),
            page_faults_delta=int(d.get("page_faults_delta", 0)),
            cpu_core_peaks=list(d.get("cpu_core_peaks", [])),
        )
