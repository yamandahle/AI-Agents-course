"""Unit tests for latex/latex_templates.py."""
from article_writer.latex.latex_templates import (
    BIBLIOGRAPHY_SECTION,
    COVER_PAGE,
    HEADER_FOOTER_SETUP,
    LUALATEX_PREAMBLE,
    TOC_SECTION,
)

_REQUIRED_PACKAGES = [
    "polyglossia", "fontspec", "geometry", "hyperref",
    "biblatex", "tikz", "graphicx", "booktabs",
    "amsmath", "fancyhdr", "listings",
]


def test_preamble_contains_all_required_packages() -> None:
    for pkg in _REQUIRED_PACKAGES:
        assert pkg in LUALATEX_PREAMBLE, f"Missing package: {pkg}"


def test_preamble_starts_with_documentclass() -> None:
    assert LUALATEX_PREAMBLE.strip().startswith(r"\documentclass")


def test_cover_page_has_all_placeholders() -> None:
    for field in ("{title}", "{author}", "{date}", "{course}", "{lecturer}"):
        assert field in COVER_PAGE


def test_header_footer_uses_fancyhdr() -> None:
    assert "fancy" in HEADER_FOOTER_SETUP


def test_bibliography_section_has_printbibliography() -> None:
    assert r"\printbibliography" in BIBLIOGRAPHY_SECTION


def test_toc_section_has_tableofcontents() -> None:
    assert r"\tableofcontents" in TOC_SECTION
