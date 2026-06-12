"""Base agent mixin — shared skill loading and task logging for all article-writer agents."""
from __future__ import annotations

from pathlib import Path

from article_writer.shared.constants import SKILLS_DIR
from article_writer.shared.logger import get_logger

logger = get_logger(__name__)


class BaseAgentMixin:
    """Mixin providing skill loading and task lifecycle logging.

    Usage: class MyAgent(BaseAgentMixin): ...
    """

    def _load_skills(self, skill_name: str) -> str:
        """Read SKILL.md from skills/<skill_name>/ and return its content."""
        skill_path = Path(SKILLS_DIR) / skill_name / "SKILL.md"
        try:
            content = skill_path.read_text(encoding="utf-8")
            logger.info("Loaded skill '%s' (%d chars)", skill_name, len(content))
            return content
        except FileNotFoundError:
            logger.warning("Skill file not found: %s — continuing without it", skill_path)
            return ""

    def _log_task_start(self, task_name: str) -> None:
        logger.info("[TASK START] %s", task_name)

    def _log_task_end(self, task_name: str, result_preview: str = "") -> None:
        logger.info("[TASK END] %s — result_preview='%s'", task_name, result_preview[:80])

    def build_backstory(self, base_backstory: str, skill_name: str) -> str:
        """Append loaded skill content to a base backstory string."""
        skill_content = self._load_skills(skill_name)
        if skill_content:
            return f"{base_backstory}\n\n--- SKILL CONTEXT ---\n{skill_content}"
        return base_backstory
