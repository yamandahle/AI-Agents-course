"""Print a cost/latency breakdown from results/metrics.jsonl."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from article_writer.shared.metrics_tracker import MetricsTracker


def main() -> None:
    metrics_path = Path("results/metrics.jsonl")
    tracker = MetricsTracker(path=metrics_path)
    if not metrics_path.exists():
        print("No metrics file found. Run the pipeline first.")
        return

    import json
    records: list[dict] = []
    with metrics_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    cumulative_cost = 0.0
    print(f"{'Step':<30} {'Model':<25} {'Latency(ms)':<14} {'Tokens':<10} {'Cost $':<12} {'Cumulative $'}")
    print("-" * 110)
    for r in records:
        cumulative_cost += r.get("cost_usd", 0.0)
        print(
            f"{r.get('step',''):<30} {r.get('model',''):<25} "
            f"{r.get('latency_ms',0):<14} {r.get('total_tokens',0):<10} "
            f"{r.get('cost_usd',0.0):<12.6f} {cumulative_cost:.6f}"
        )
    summary = tracker.summary()
    print(f"\nTotals: {summary['steps']} steps | "
          f"{summary['total_tokens']} tokens | "
          f"${summary['total_cost_usd']:.4f} cost | "
          f"{summary['total_latency_ms']}ms latency")


if __name__ == "__main__":
    main()
