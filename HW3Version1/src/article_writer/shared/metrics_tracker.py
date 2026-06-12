"""Per-step latency, token, and cost logger — writes to metrics.jsonl."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


_DEFAULT_PATH = Path("results/metrics.jsonl")


class MetricsTracker:
    """Append-only JSONL recorder for cost and latency metrics."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path or os.getenv("METRICS_FILE", str(_DEFAULT_PATH)))
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        step: str,
        model: str,
        latency_ms: int,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        extra: dict | None = None,
    ) -> None:
        record = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "step": step,
            "model": model,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost_usd, 6),
        }
        if extra:
            record.update(extra)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def summary(self) -> dict:
        if not self._path.exists():
            return {"steps": 0, "total_tokens": 0, "total_cost_usd": 0.0, "total_latency_ms": 0}
        total_tokens = 0
        total_cost = 0.0
        total_latency = 0
        steps = 0
        with self._path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                total_tokens += rec.get("total_tokens", 0)
                total_cost += rec.get("cost_usd", 0.0)
                total_latency += rec.get("latency_ms", 0)
                steps += 1
        return {
            "steps": steps,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_latency_ms": total_latency,
        }
