"""MetricsBuffer and VRAMSpikeEvent — thread-safe sample store for the monitor."""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class VRAMSpikeEvent:
    """Records a sudden increase in VRAM allocation exceeding the threshold."""

    timestamp: float
    prev_vram_mb: float
    curr_vram_mb: float
    delta_mb: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return {
            "timestamp": self.timestamp,
            "prev_vram_mb": self.prev_vram_mb,
            "curr_vram_mb": self.curr_vram_mb,
            "delta_mb": self.delta_mb,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> VRAMSpikeEvent:
        """Deserialize from a plain dictionary."""
        return cls(
            timestamp=float(d["timestamp"]),
            prev_vram_mb=float(d["prev_vram_mb"]),
            curr_vram_mb=float(d["curr_vram_mb"]),
            delta_mb=float(d["delta_mb"]),
        )

    def is_significant(self, threshold_mb: float) -> bool:
        """Return True when the VRAM delta exceeds the given threshold."""
        return self.delta_mb > threshold_mb


class MetricsBuffer:
    """Thread-safe deque-backed store for per-sample metric dictionaries."""

    def __init__(self) -> None:
        self._data: deque[dict[str, Any]] = deque()
        self._lock = threading.Lock()

    def append(self, sample: dict[str, Any]) -> None:
        """Append one sample dict to the buffer."""
        with self._lock:
            self._data.append(sample)

    def to_list(self) -> list[dict[str, Any]]:
        """Return a snapshot copy of all stored samples."""
        with self._lock:
            return list(self._data)

    def clear(self) -> None:
        """Remove all stored samples."""
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)
