"""Build, label, and split the eval dataset from extracted MDPI articles.

Resumable: labels are checkpointed to eval_dataset/checkpoint.jsonl one at a time.
Re-running the script skips already-labeled articles and picks up where it left off.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path

from article_writer.shared.llm_client import LLMClient
from article_writer.eval.article_extractor import ExtractedArticle

_LABEL_SYSTEM = """\
You are an academic quality assessor for MDPI journal articles.
Given an article, decide if it PASSES or FAILS quality standards.
PASS = well-structured, clear contributions, adequate citations, IMRAD format followed.
FAIL = missing sections, unsupported claims, poor methodology description.

Respond with ONLY this JSON:
{
  "label": "PASS" | "FAIL",
  "critique": "<exactly 3 sentences explaining the verdict>"
}
"""

_INTER_CALL_DELAY = 65  # seconds — stays under free-tier RPM (1 RPM free tier)
_CHECKPOINT_FILE = Path("eval_dataset/checkpoint.jsonl")


@dataclass
class LabelledSample:
    article_id: str
    filename: str
    full_text: str
    abstract: str
    keywords: list[str]
    label: str
    critique: str
    split: str = "train"


class DatasetBuilder:
    """Reverse-engineers articles into labelled samples and splits into train/dev/test."""

    def __init__(self, llm: LLMClient | None = None, seed: int = 42) -> None:
        self._llm = llm or LLMClient()
        self._seed = seed

    def build_from_articles(
        self,
        articles: list[ExtractedArticle],
        output_dir: str | Path = "eval_dataset",
    ) -> dict[str, list[LabelledSample]]:
        out_dir = Path(output_dir)
        already_labelled = self._load_checkpoint()
        labelled_filenames = {s["filename"] for s in already_labelled}
        random.seed(self._seed)
        samples: list[LabelledSample] = [LabelledSample(**s) for s in already_labelled]

        for idx, art in enumerate(articles):
            if art.filename in labelled_filenames:
                print(f"[dataset_builder] skip (cached) {art.filename}")
                continue
            if samples:
                print(f"[dataset_builder] waiting {_INTER_CALL_DELAY}s before next API call...")
                time.sleep(_INTER_CALL_DELAY)
            done = len(labelled_filenames) + (len(samples) - len(already_labelled))
            print(f"[dataset_builder] labelling {done+1}/{len(articles)}: {art.filename}")
            label, critique = self._label(art)
            print(f"  → {label}: {critique[:80]}...")
            sample = LabelledSample(
                article_id=f"art_{idx:03d}",
                filename=art.filename,
                full_text=art.full_text[:8000],
                abstract=art.abstract,
                keywords=art.keywords,
                label=label,
                critique=critique,
            )
            samples.append(sample)
            self._save_checkpoint(sample)

        random.shuffle(samples)
        splits = self._split(samples)
        self._save_splits(splits, out_dir)
        return splits

    def _label(self, art: ExtractedArticle) -> tuple[str, str]:
        user = (
            f"Abstract: {art.abstract}\n\n"
            f"Keywords: {', '.join(art.keywords)}\n\n"
            f"Article excerpt:\n{art.full_text[:4000]}"
        )
        resp = self._llm.complete(
            system=_LABEL_SYSTEM, user=user,
            step=f"label:{art.filename}", temperature=0.1,
        )
        raw = resp.text.strip()
        start, end = raw.find("{"), raw.rfind("}") + 1
        try:
            data = json.loads(raw[start:end])
            return data.get("label", "FAIL"), data.get("critique", "")
        except Exception:
            return "FAIL", "Could not parse labeller output."

    def _load_checkpoint(self) -> list[dict]:
        if not _CHECKPOINT_FILE.exists():
            return []
        records: list[dict] = []
        with _CHECKPOINT_FILE.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def _save_checkpoint(self, sample: LabelledSample) -> None:
        _CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _CHECKPOINT_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")

    def _split(self, samples: list[LabelledSample]) -> dict[str, list[LabelledSample]]:
        n = len(samples)
        n_test = max(2, n // 7)
        n_dev = max(2, n // 7)
        test = samples[:n_test]
        dev = samples[n_test:n_test + n_dev]
        train = samples[n_test + n_dev:]
        for s in train:
            s.split = "train"
        for s in dev:
            s.split = "dev"
        for s in test:
            s.split = "test"
        return {"train": train, "dev": dev, "test": test}

    def _save_splits(self, splits: dict[str, list[LabelledSample]], out_dir: Path) -> None:
        (out_dir / "splits").mkdir(parents=True, exist_ok=True)
        for split_name, split_samples in splits.items():
            path = out_dir / "splits" / f"{split_name}.jsonl"
            with path.open("w", encoding="utf-8") as fh:
                for s in split_samples:
                    fh.write(json.dumps(asdict(s), ensure_ascii=False) + "\n")
