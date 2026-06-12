"""CLI script: extract MDPI PDFs → label → split → run F1 judge loop."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from article_writer.eval.article_extractor import ArticleExtractor
from article_writer.eval.dataset_builder import DatasetBuilder
from article_writer.eval.judge_loop import JudgeLoop
from article_writer.shared.llm_client import LLMClient

# Use generic quality guideline for eval, NOT the topic-specific article guideline.
# Real MDPI articles would fail coverage checks against our specific topic guideline.
_EVAL_GUIDELINE = Path("eval_dataset/quality_guideline.md")
_EVAL_RESEARCH = Path("")  # no specific research for generic quality eval


def main() -> None:
    raw_dir = Path("eval_dataset/raw")
    out_dir = Path("eval_dataset")

    print(f"[eval] Scanning {raw_dir} for MDPI PDFs...")
    extractor = ArticleExtractor()
    articles = extractor.extract_directory(raw_dir)
    if not articles:
        print("[eval] No valid PDFs found in eval_dataset/raw/ — checking few_shot_examples/...")
        articles = extractor.extract_directory(Path("few_shot_examples"))

    print(f"[eval] Extracted {len(articles)} articles")
    if not articles:
        print("[eval] No articles found. Exiting.")
        return

    llm = LLMClient()
    print("[eval] Labelling articles (PASS/FAIL)...")
    builder = DatasetBuilder(llm=llm)
    splits = builder.build_from_articles(articles, output_dir=out_dir)
    for name, samples in splits.items():
        print(f"[eval] Split '{name}': {len(samples)} samples")

    def load_jsonl(p: Path) -> list[dict]:
        if not p.exists():
            return []
        with p.open(encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    dev_samples = load_jsonl(out_dir / "splits" / "dev.jsonl")
    test_samples = load_jsonl(out_dir / "splits" / "test.jsonl")

    if not dev_samples or not test_samples:
        print("[eval] Not enough samples for judge loop. Need ≥1 in dev and test splits.")
        return

    guideline = _EVAL_GUIDELINE.read_text(encoding="utf-8") if _EVAL_GUIDELINE.exists() else ""
    print(f"[eval] Running judge loop on {len(dev_samples)} dev / {len(test_samples)} test")
    print(f"[eval] Using guideline: {_EVAL_GUIDELINE}")

    loop = JudgeLoop(
        llm=llm,
        guideline_path=_EVAL_GUIDELINE,
        research_path=_EVAL_RESEARCH,
    )
    result = loop.run(dev_samples, test_samples)
    print(result["test_report"])
    print(f"[eval] Done. Dev F1 history: {result['dev_f1_history']}")
    print(f"[eval] Final test F1: {result['test_f1']:.4f}")

    summary_path = out_dir / "judge_results.json"
    summary_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"[eval] Results saved to {summary_path}")


if __name__ == "__main__":
    main()
