"""Phase 1 — loads all context files and builds the unified writer context string."""
from __future__ import annotations

from pathlib import Path

from article_writer.shared.constants import (
    DEFAULT_ENCODING,
    FEW_SHOT_DIR,
    GUIDELINE_PATH,
    PROFILES_DIR,
    RESEARCH_ARTIFACT_PATH,
)
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)

_PROFILE_FILES = ("Structure.md", "Terminology.md", "Characters.md")


class ContextLoader:
    """Loads and combines all writing context files into a single structured string."""

    def __init__(
        self,
        guideline_path: str = GUIDELINE_PATH,
        research_path: str = RESEARCH_ARTIFACT_PATH,
        profiles_dir: str = PROFILES_DIR,
        few_shot_dir: str = FEW_SHOT_DIR,
    ) -> None:
        self._guideline_path = Path(guideline_path)
        self._research_path = Path(research_path)
        self._profiles_dir = Path(profiles_dir)
        self._few_shot_dir = Path(few_shot_dir)

    def load_guideline(self) -> str:
        return self._read_required(self._guideline_path, "guideline")

    def load_research(self) -> str:
        return self._read_required(self._research_path, "research artifact")

    def load_profiles(self) -> str:
        parts: list[str] = []
        for name in _PROFILE_FILES:
            path = self._profiles_dir / name
            try:
                content = path.read_text(encoding=DEFAULT_ENCODING)
                logger.info("Loaded profile '%s' (%d chars)", name, len(content))
                parts.append(f"### {name}\n{content}")
            except FileNotFoundError:
                logger.warning("Profile file missing: %s", path)
        return "\n\n".join(parts)

    def load_few_shots(self) -> str:
        from article_writer.writing.few_shot_loader import FewShotLoader
        loader = FewShotLoader(self._few_shot_dir)
        block = loader.build_context_block()
        logger.info("Loaded %d few-shot examples from %s", len(loader.load_all()), self._few_shot_dir)
        return block

    def build_writer_context(self) -> str:
        profiles = self.load_profiles()
        few_shots = self.load_few_shots()
        guideline = self.load_guideline()
        research = self.load_research()
        return (
            f"## WRITING PROFILES (HOW TO WRITE)\n{profiles}\n\n"
            f"## FEW-SHOT EXAMPLES\n{few_shots}\n\n"
            f"## ARTICLE GUIDELINE (WHAT TO WRITE)\n{guideline}\n\n"
            f"## RESEARCH MATERIAL\n{research}"
        )

    def _read_required(self, path: Path, label: str) -> str:
        if not path.exists():
            raise FileNotFoundError(f"Required {label} file not found: {path}")
        content = path.read_text(encoding=DEFAULT_ENCODING)
        logger.info("Loaded %s '%s' (%d chars)", label, path.name, len(content))
        return content
