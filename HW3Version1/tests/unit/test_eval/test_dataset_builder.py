"""Tests for eval/dataset_builder.py — labels articles and splits into train/dev/test."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from article_writer.eval.dataset_builder import DatasetBuilder, LabelledSample
from article_writer.eval.article_extractor import ExtractedArticle


def _make_article(filename: str = "art.pdf") -> ExtractedArticle:
    return ExtractedArticle(
        filename=filename,
        page_count=16,
        full_text="Full text of the article " * 50,
        abstract="Abstract text.",
        keywords=["AI", "health"],
    )


def _mock_llm(label: str = "PASS") -> MagicMock:
    resp = MagicMock()
    resp.text = json.dumps({"label": label, "critique": "Good. Clear. Well structured."})
    llm = MagicMock()
    llm.complete.return_value = resp
    return llm


def test_label_returns_pass_or_fail() -> None:
    builder = DatasetBuilder(llm=_mock_llm("PASS"))
    label, critique = builder._label(_make_article())
    assert label == "PASS"
    assert len(critique) > 0


def test_label_fallback_on_bad_json() -> None:
    resp = MagicMock()
    resp.text = "not valid json at all"
    llm = MagicMock()
    llm.complete.return_value = resp
    builder = DatasetBuilder(llm=llm)
    label, _ = builder._label(_make_article())
    assert label == "FAIL"


def test_split_gives_at_least_2_in_dev_and_test() -> None:
    samples = [
        LabelledSample(f"art_{i:03d}", f"f{i}.pdf", "text", "abstract", [], "PASS", "Good.")
        for i in range(20)
    ]
    builder = DatasetBuilder(llm=_mock_llm())
    splits = builder._split(samples)
    assert len(splits["dev"]) >= 2
    assert len(splits["test"]) >= 2


def test_split_sets_correct_split_field() -> None:
    samples = [
        LabelledSample(f"art_{i:03d}", f"f{i}.pdf", "text", "abstract", [], "PASS", "Good.")
        for i in range(20)
    ]
    builder = DatasetBuilder(llm=_mock_llm())
    splits = builder._split(samples)
    assert all(s.split == "train" for s in splits["train"])
    assert all(s.split == "dev" for s in splits["dev"])
    assert all(s.split == "test" for s in splits["test"])


def test_save_splits_writes_jsonl_files(tmp_path: Path) -> None:
    sample = LabelledSample("art_000", "f0.pdf", "text", "abstract", [], "PASS", "Good.")
    splits = {"train": [sample], "dev": [sample], "test": [sample]}
    builder = DatasetBuilder(llm=_mock_llm())
    builder._save_splits(splits, tmp_path)
    for name in ("train", "dev", "test"):
        f = tmp_path / "splits" / f"{name}.jsonl"
        assert f.exists()
        records = [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines()]
        assert len(records) == 1
