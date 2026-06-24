"""CellResult — one (model, framework, quant) evaluation outcome."""

from __future__ import annotations

from dataclasses import dataclass

from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.runner_protocol import InferenceResult


@dataclass
class CellResult:
    """Captures inference output, OS metrics, and status for a single eval cell."""

    cell_id: str
    inference: InferenceResult
    metrics: MetricsSnapshot
    started_at: float
    finished_at: float
    cpu_only: bool = False
    failed: bool = False
    error_message: str = ""

    @property
    def duration_s(self) -> float:
        """Wall-clock seconds from cell start to finish."""
        return self.finished_at - self.started_at

    def to_dict(self) -> dict:
        """Serialize to a JSON-safe dictionary."""
        return {
            "cell_id": self.cell_id,
            "inference": self.inference.to_dict(),
            "metrics": self.metrics.to_dict(),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "cpu_only": self.cpu_only,
            "failed": self.failed,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CellResult:
        """Deserialize from a plain dictionary."""
        return cls(
            cell_id=d["cell_id"],
            inference=InferenceResult.from_dict(d.get("inference", {})),
            metrics=MetricsSnapshot.from_dict(d.get("metrics", {})),
            started_at=float(d.get("started_at", 0.0)),
            finished_at=float(d.get("finished_at", 0.0)),
            cpu_only=bool(d.get("cpu_only", False)),
            failed=bool(d.get("failed", False)),
            error_message=str(d.get("error_message", "")),
        )
