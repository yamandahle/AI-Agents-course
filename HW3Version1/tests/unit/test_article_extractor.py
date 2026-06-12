"""Unit tests for ArticleExtractor (eval/article_extractor.py)."""
from pathlib import Path

import pytest

from article_writer.eval.article_extractor import ArticleExtractor, ExtractedArticle


@pytest.fixture
def real_pdfs():
    base = Path("few_shot_examples")
    return {
        "behavsci": base / "behavsci-16-00973.pdf",
        "foods": base / "foods-15-02113.pdf",
        "animals": base / "animals-16-01806.pdf",
    }


def test_extract_nonexistent_pdf_raises():
    extractor = ArticleExtractor()
    with pytest.raises(RuntimeError):
        extractor.extract("/nonexistent/path/article.pdf")


def test_extract_directory_empty(tmp_path):
    extractor = ArticleExtractor()
    results = extractor.extract_directory(tmp_path)
    assert results == []


def test_extracted_article_has_filename(real_pdfs):
    if not real_pdfs["animals"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    art = extractor.extract(real_pdfs["animals"])
    assert art.filename == "animals-16-01806.pdf"


def test_extracted_article_page_count_animals(real_pdfs):
    if not real_pdfs["animals"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    art = extractor.extract(real_pdfs["animals"])
    assert art.page_count == 18


def test_extracted_article_page_count_foods(real_pdfs):
    if not real_pdfs["foods"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    art = extractor.extract(real_pdfs["foods"])
    assert art.page_count == 20


def test_extracted_article_page_count_behavsci(real_pdfs):
    if not real_pdfs["behavsci"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    art = extractor.extract(real_pdfs["behavsci"])
    assert art.page_count == 16


def test_parse_abstract_not_empty(real_pdfs):
    if not real_pdfs["animals"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    art = extractor.extract(real_pdfs["animals"])
    assert len(art.abstract) > 50


def test_parse_keywords_not_empty(real_pdfs):
    if not real_pdfs["animals"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    art = extractor.extract(real_pdfs["animals"])
    assert len(art.keywords) >= 3


def test_extract_directory_filters_by_page_count(real_pdfs):
    if not real_pdfs["animals"].exists():
        pytest.skip("MDPI PDFs not available in test environment")
    extractor = ArticleExtractor()
    results = extractor.extract_directory(real_pdfs["animals"].parent)
    for art in results:
        assert 13 <= art.page_count <= 20
