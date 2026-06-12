"""BiDi handler — Hebrew-English bidirectional text management for LuaLaTeX + polyglossia."""
from __future__ import annotations

_HEBREW_START = 0x0590
_HEBREW_END = 0x05FF


class BiDiHandler:
    """Manages RTL/LTR switching for Hebrew-English mixed LaTeX documents."""

    @staticmethod
    def contains_hebrew(text: str) -> bool:
        """Return True if text contains any Hebrew Unicode character."""
        return any(_HEBREW_START <= ord(c) <= _HEBREW_END for c in text)

    @staticmethod
    def wrap_rtl(text: str) -> str:
        """Wrap a block of text in polyglossia RTL environment."""
        return f"\\begin{{hebrew}}\n{text}\n\\end{{hebrew}}"

    @staticmethod
    def wrap_ltr(text: str) -> str:
        """Wrap a block of text in polyglossia LTR environment."""
        return f"\\begin{{english}}\n{text}\n\\end{{english}}"

    @staticmethod
    def inline_ltr(text: str) -> str:
        """Wrap an inline LTR fragment inside an RTL context."""
        return f"\\textLR{{{text}}}"

    @staticmethod
    def inject_bidi_chapter(chapter_content: str) -> str:
        """Auto-detect per-sentence direction and wrap appropriately."""
        sentences = chapter_content.split(". ")
        parts: list[str] = []
        for sentence in sentences:
            stripped = sentence.strip()
            if not stripped:
                continue
            if BiDiHandler.contains_hebrew(stripped):
                parts.append(BiDiHandler.wrap_rtl(stripped + "."))
            else:
                parts.append(BiDiHandler.wrap_ltr(stripped + "."))
        return "\n\n".join(parts)

    @staticmethod
    def polyglossia_setup() -> str:
        """Return polyglossia language configuration for Hebrew + English."""
        return (
            "\\setmainlanguage{english}\n"
            "\\setotherlanguage{hebrew}\n"
            "\\newfontfamily\\hebrewfont[Script=Hebrew]{FreeSans}\n"
        )
