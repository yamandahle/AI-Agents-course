"""CLI entry point — orchestrates the full article-writing pipeline via ArticleWriterSDK."""
from __future__ import annotations

import argparse
import sys

from article_writer.sdk.sdk import ArticleWriterSDK
from article_writer.shared.metrics_tracker import MetricsTracker


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Article Writer — multi-agent pipeline")
    parser.add_argument("--topic",
                        help="Article topic (auto-generates guideline.md from this)")
    parser.add_argument("--guideline", default="data/guideline.md",
                        help="Path to article guideline (used when --topic is not given)")
    parser.add_argument("--research", default="data/research.md",
                        help="Path to research artifact")
    parser.add_argument("--few-shots", default="few_shot_examples",
                        help="Directory of few-shot examples (PDF or MD)")
    parser.add_argument("--review-iterations", type=int, default=None,
                        help="Number of reviewer-editor cycles (2-4, default from config)")
    parser.add_argument(
        "--mode",
        choices=["research", "write", "full"],
        default="full",
        help="Pipeline mode: research only, write only (needs research.md), or full",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    sdk = ArticleWriterSDK()
    metrics = MetricsTracker()
    guideline_path = args.guideline

    try:
        if args.topic:
            print(f"Generating guideline for topic: {args.topic!r}")
            guideline_path = str(sdk.generate_guideline(args.topic))
            print(f"Guideline written: {guideline_path}")

        if args.mode in ("research", "full"):
            research_path = sdk.start_research_session(guideline_path)
            print(f"Research complete: {research_path}")

        if args.mode in ("write", "full"):
            draft_path = sdk.start_writing_session(
                guideline_path=guideline_path,
                research_path=args.research,
                few_shot_dir=args.few_shots,
            )
            print(f"Draft generated: {draft_path}")

            final_draft = sdk.run_review_loop(
                draft_path=str(draft_path),
                iterations=args.review_iterations,
            )
            print(f"Review loop complete: {final_draft}")

            try:
                pdf_path = sdk.compile_to_pdf(str(final_draft))
                print(f"PDF compiled: {pdf_path}")
            except FileNotFoundError as exc:
                print(f"Warning: LaTeX compiler not found — skipping PDF step ({exc})")
                print(f"To compile: lualatex {final_draft}")

        summary = metrics.summary()
        if summary["steps"] > 0:
            print(f"\nPipeline summary: {summary['steps']} LLM calls | "
                  f"${summary['total_cost_usd']:.4f} cost | "
                  f"{summary['total_tokens']} tokens | "
                  f"{summary['total_latency_ms']}ms total")
            print("Traces: results/traces.jsonl | Metrics: results/metrics.jsonl")

    except FileNotFoundError as exc:
        print(f"Error: required file not found — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
