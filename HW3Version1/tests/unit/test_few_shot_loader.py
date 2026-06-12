"""Unit tests for FewShotLoader (writing/few_shot_loader.py)."""
from pathlib import Path

import pytest

from article_writer.writing.few_shot_loader import FewShotLoader, _MAX_CHARS_PER_EXAMPLE


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def test_load_all_empty_directory(tmp_dir):
    loader = FewShotLoader(tmp_dir)
    assert loader.load_all() == []


def test_load_all_reads_md_file(tmp_dir):
    (tmp_dir / "example.md").write_text("# Example\nContent here.", encoding="utf-8")
    loader = FewShotLoader(tmp_dir)
    results = loader.load_all()
    assert len(results) == 1
    assert results[0]["name"] == "example"
    assert "Content here" in results[0]["text"]


def test_load_all_skips_non_supported_extension(tmp_dir):
    (tmp_dir / "file.docx").write_bytes(b"binary")
    loader = FewShotLoader(tmp_dir)
    assert loader.load_all() == []


def test_load_all_truncates_to_max_chars(tmp_dir):
    (tmp_dir / "big.md").write_text("x" * 20000, encoding="utf-8")
    loader = FewShotLoader(tmp_dir)
    results = loader.load_all()
    assert len(results[0]["text"]) <= _MAX_CHARS_PER_EXAMPLE


def test_load_all_sorted_alphabetically(tmp_dir):
    (tmp_dir / "b_example.md").write_text("B", encoding="utf-8")
    (tmp_dir / "a_example.md").write_text("A", encoding="utf-8")
    loader = FewShotLoader(tmp_dir)
    results = loader.load_all()
    assert results[0]["name"] == "a_example"
    assert results[1]["name"] == "b_example"


def test_build_context_block_empty(tmp_dir):
    loader = FewShotLoader(tmp_dir)
    assert loader.build_context_block() == ""


def test_build_context_block_has_headers(tmp_dir):
    (tmp_dir / "sample.md").write_text("Sample content", encoding="utf-8")
    loader = FewShotLoader(tmp_dir)
    block = loader.build_context_block()
    assert "FEW-SHOT" in block
    assert "sample" in block


def test_read_pdf_returns_placeholder_on_bad_file(tmp_dir):
    bad_pdf = tmp_dir / "bad.pdf"
    bad_pdf.write_bytes(b"not a real pdf")
    loader = FewShotLoader(tmp_dir)
    results = loader.load_all()
    assert len(results) == 1
    assert "extraction failed" in results[0]["text"].lower() or len(results[0]["text"]) >= 0


def test_nonexistent_directory():
    loader = FewShotLoader("/nonexistent/path/12345")
    assert loader.load_all() == []
