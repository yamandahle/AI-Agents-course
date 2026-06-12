"""Unit tests for writing/context_loader.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from article_writer.writing.context_loader import ContextLoader


def test_build_writer_context_contains_all_sections(tmp_path: Path) -> None:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "guideline.md").write_text("## Topic\nTest", encoding="utf-8")
    (tmp_path / "data" / "research.md").write_text("# Research\nFact 1", encoding="utf-8")
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    for name in ("Structure.md", "Terminology.md", "Characters.md"):
        (profiles / name).write_text(f"# {name}\nContent", encoding="utf-8")
    (tmp_path / "few_shot_examples").mkdir()
    loader = ContextLoader(
        guideline_path=str(tmp_path / "data" / "guideline.md"),
        research_path=str(tmp_path / "data" / "research.md"),
        profiles_dir=str(profiles),
        few_shot_dir=str(tmp_path / "few_shot_examples"),
    )
    ctx = loader.build_writer_context()
    assert "## WRITING PROFILES" in ctx
    assert "## ARTICLE GUIDELINE" in ctx
    assert "## RESEARCH MATERIAL" in ctx


def test_load_guideline_raises_when_missing(tmp_path: Path) -> None:
    loader = ContextLoader(
        guideline_path=str(tmp_path / "nonexistent.md"),
        research_path=str(tmp_path / "research.md"),
    )
    with pytest.raises(FileNotFoundError):
        loader.load_guideline()


def test_profiles_appear_before_guideline(tmp_path: Path) -> None:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "guideline.md").write_text("guide", encoding="utf-8")
    (tmp_path / "data" / "research.md").write_text("research", encoding="utf-8")
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    for name in ("Structure.md", "Terminology.md", "Characters.md"):
        (profiles / name).write_text("profile content", encoding="utf-8")
    (tmp_path / "few_shot_examples").mkdir()
    loader = ContextLoader(
        guideline_path=str(tmp_path / "data" / "guideline.md"),
        research_path=str(tmp_path / "data" / "research.md"),
        profiles_dir=str(profiles),
        few_shot_dir=str(tmp_path / "few_shot_examples"),
    )
    ctx = loader.build_writer_context()
    profiles_idx = ctx.index("## WRITING PROFILES")
    guideline_idx = ctx.index("## ARTICLE GUIDELINE")
    assert profiles_idx < guideline_idx
