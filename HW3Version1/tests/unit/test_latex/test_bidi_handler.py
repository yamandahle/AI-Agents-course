"""Unit tests for latex/bidi_handler.py."""
from article_writer.latex.bidi_handler import BiDiHandler


def test_contains_hebrew_detects_hebrew_chars() -> None:
    assert BiDiHandler.contains_hebrew("שלום") is True


def test_contains_hebrew_returns_false_for_ascii() -> None:
    assert BiDiHandler.contains_hebrew("Hello World") is False


def test_contains_hebrew_mixed_text() -> None:
    assert BiDiHandler.contains_hebrew("Hello שלום") is True


def test_wrap_rtl_produces_hebrew_env() -> None:
    result = BiDiHandler.wrap_rtl("שלום")
    assert r"\begin{hebrew}" in result
    assert r"\end{hebrew}" in result
    assert "שלום" in result


def test_wrap_ltr_produces_english_env() -> None:
    result = BiDiHandler.wrap_ltr("Hello")
    assert r"\begin{english}" in result
    assert r"\end{english}" in result


def test_inject_bidi_chapter_wraps_hebrew() -> None:
    content = "שלום עולם"
    result = BiDiHandler.inject_bidi_chapter(content)
    assert r"\begin{hebrew}" in result


def test_inject_bidi_chapter_wraps_english() -> None:
    content = "Hello World"
    result = BiDiHandler.inject_bidi_chapter(content)
    assert r"\begin{english}" in result


def test_polyglossia_setup_contains_setmainlanguage() -> None:
    setup = BiDiHandler.polyglossia_setup()
    assert r"\setmainlanguage" in setup
    assert "english" in setup
