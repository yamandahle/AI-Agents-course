"""Unit tests for agents/base_agent.py."""
from __future__ import annotations

from pathlib import Path

from article_writer.agents.base_agent import BaseAgentMixin


def test_load_skills_returns_empty_on_missing_dir() -> None:
    mixin = BaseAgentMixin()
    result = mixin._load_skills("nonexistent-skill")
    assert result == ""


def test_load_skills_reads_skill_md(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    skills_dir = tmp_path / "skills" / "test-skill"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# Test Skill\nInstructions.", encoding="utf-8")
    mixin = BaseAgentMixin()
    result = mixin._load_skills("test-skill")
    assert "Test Skill" in result
    assert "Instructions" in result


def test_build_backstory_appends_skill(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    skills_dir = tmp_path / "skills" / "my-skill"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("Skill content here.", encoding="utf-8")
    mixin = BaseAgentMixin()
    backstory = mixin.build_backstory("Base backstory.", "my-skill")
    assert "Base backstory." in backstory
    assert "Skill content here." in backstory


def test_build_backstory_returns_base_when_skill_missing() -> None:
    mixin = BaseAgentMixin()
    backstory = mixin.build_backstory("Base only.", "no-such-skill")
    assert backstory == "Base only."


def test_log_task_start_does_not_raise() -> None:
    mixin = BaseAgentMixin()
    mixin._log_task_start("test-task")


def test_log_task_end_does_not_raise() -> None:
    mixin = BaseAgentMixin()
    mixin._log_task_end("test-task", "preview")
