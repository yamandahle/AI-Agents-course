"""Print a per-step summary of results/traces.jsonl."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from article_writer.shared.tracer import Tracer


def main() -> None:
    traces_path = Path("results/traces.jsonl")
    tracer = Tracer(path=traces_path)
    records = tracer.read_all()
    if not records:
        print("No trace records found. Run the pipeline first.")
        return
    print(f"{'Step':<30} {'Model':<25} {'In':<8} {'Out':<8} {'Input snippet'}")
    print("-" * 100)
    for r in records:
        snippet = r.get("input", "")[:60].replace("\n", " ")
        print(
            f"{r.get('step',''):<30} {r.get('model',''):<25} "
            f"{r.get('input_tokens',0):<8} {r.get('output_tokens',0):<8} {snippet}"
        )
    print(f"\nTotal: {len(records)} trace records in {traces_path}")


if __name__ == "__main__":
    main()
