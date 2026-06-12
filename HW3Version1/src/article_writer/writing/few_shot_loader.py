"""PDF-aware few-shot loader — reads .pdf files via fitz, plain text for .md files."""
from __future__ import annotations

from pathlib import Path


_MAX_CHARS_PER_EXAMPLE = 8000
_HEADER_FMT = "=== FEW-SHOT EXAMPLE: {name} ===\n"


class FewShotLoader:
    """Loads few-shot examples from a directory; supports both .md and .pdf files."""

    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)

    def load_all(self) -> list[dict[str, str]]:
        examples: list[dict[str, str]] = []
        if not self._dir.exists():
            return examples
        for path in sorted(self._dir.iterdir()):
            if path.suffix == ".pdf":
                text = self._read_pdf(path)
            elif path.suffix in {".md", ".txt"}:
                text = path.read_text(encoding="utf-8")
            else:
                continue
            if text.strip():
                examples.append({"name": path.stem, "text": text[:_MAX_CHARS_PER_EXAMPLE]})
        return examples

    def build_context_block(self) -> str:
        examples = self.load_all()
        if not examples:
            return ""
        parts = ["## FEW-SHOT EXAMPLES (MDPI Article Style)\n"]
        for ex in examples:
            parts.append(_HEADER_FMT.format(name=ex["name"]))
            parts.append(ex["text"])
            parts.append("\n")
        return "\n".join(parts)

    def _read_pdf(self, path: Path) -> str:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            pages: list[str] = []
            for page in doc:
                pages.append(page.get_text())
            doc.close()
            return "\n".join(pages)
        except Exception as exc:
            return f"[PDF extraction failed for {path.name}: {exc}]"
