"""Extract structured text from MDPI PDF articles using PyMuPDF (fitz)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


_MIN_PAGES = 13
_MAX_PAGES = 20


@dataclass
class ExtractedArticle:
    filename: str
    page_count: int
    full_text: str
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)


class ArticleExtractor:
    """Converts MDPI PDFs into ExtractedArticle objects for eval dataset construction."""

    def extract(self, pdf_path: str | Path) -> ExtractedArticle:
        path = Path(pdf_path)
        try:
            import fitz
            doc = fitz.open(str(path))
        except Exception as exc:
            raise RuntimeError(f"Cannot open PDF {path}: {exc}") from exc

        pages = [page.get_text() for page in doc]
        doc.close()
        n_pages = len(pages)
        full_text = "\n".join(pages)
        article = ExtractedArticle(
            filename=path.name,
            page_count=n_pages,
            full_text=full_text,
        )
        self._parse_abstract(article, full_text)
        self._parse_keywords(article, full_text)
        self._parse_sections(article, full_text)
        return article

    def extract_directory(self, directory: str | Path) -> list[ExtractedArticle]:
        results: list[ExtractedArticle] = []
        for pdf in sorted(Path(directory).glob("*.pdf")):
            try:
                art = self.extract(pdf)
                if _MIN_PAGES <= art.page_count <= _MAX_PAGES:
                    results.append(art)
            except RuntimeError:
                continue
        return results

    def _parse_abstract(self, article: ExtractedArticle, text: str) -> None:
        lower = text.lower()
        start = lower.find("abstract")
        if start == -1:
            return
        chunk = text[start + 8:start + 2000]
        end = chunk.lower().find("keyword")
        article.abstract = chunk[:end].strip() if end != -1 else chunk[:500].strip()

    def _parse_keywords(self, article: ExtractedArticle, text: str) -> None:
        lower = text.lower()
        idx = lower.find("keywords")
        if idx == -1:
            return
        chunk = text[idx + 9:idx + 300]
        end = chunk.find("\n\n")
        kw_line = chunk[:end].strip() if end != -1 else chunk.strip()
        article.keywords = [k.strip() for k in kw_line.replace(";", ",").split(",") if k.strip()]

    def _parse_sections(self, article: ExtractedArticle, text: str) -> None:
        headings = ["introduction", "materials and methods", "results", "discussion", "conclusions"]
        lower = text.lower()
        positions: list[tuple[str, int]] = []
        for h in headings:
            idx = lower.find(h)
            if idx != -1:
                positions.append((h.title(), idx))
        positions.sort(key=lambda x: x[1])
        for i, (title, start) in enumerate(positions):
            end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
            article.sections[title] = text[start:end][:3000]
