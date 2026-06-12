"""Shared test fixtures for all unit and integration tests."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with guideline.md and research.md."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "guideline.md").write_text(
        "## Topic\nTest topic\n## Angle\nTest angle\n## Key Points\n- Point 1\n",
        encoding="utf-8",
    )
    (tmp_path / "data" / "research.md").write_text(
        "# Research: Test\n## Dimension 1\n- **Fact**: Test fact — **Confidence**: HIGH — **Source**: [Test](http://test.com)\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def tmp_profiles_dir(tmp_path: Path) -> Path:
    """Create temporary profiles/ with all 3 profile files."""
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "Structure.md").write_text("# Structure\nTest structure rules.", encoding="utf-8")
    (profiles / "Terminology.md").write_text("# Terminology\nTest terminology rules.", encoding="utf-8")
    (profiles / "Characters.md").write_text("# Characters\nTest voice rules.", encoding="utf-8")
    return tmp_path


@pytest.fixture
def tmp_few_shot_dir(tmp_path: Path) -> Path:
    """Create temporary few_shot_examples/ with one example."""
    fsd = tmp_path / "few_shot_examples"
    fsd.mkdir()
    (fsd / "example_intro.md").write_text("# Example\n```latex\n\\section{Intro}\nTest.\n```", encoding="utf-8")
    return tmp_path


@pytest.fixture
def sample_draft_tex(tmp_path: Path) -> Path:
    """Write a minimal compilable LaTeX draft to tmp_path/results/draft_v1.tex."""
    results = tmp_path / "results"
    results.mkdir()
    draft = (
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        "\\tableofcontents\n"
        "\\section{Introduction}\nTest content.\n"
        "\\end{document}\n"
    )
    path = results / "draft_v1.tex"
    path.write_text(draft, encoding="utf-8")
    return path


@pytest.fixture
def mock_gatekeeper() -> MagicMock:
    """Return a MagicMock that passes through api_call(*args, **kwargs)."""
    mock = MagicMock()
    mock.execute.side_effect = lambda service, fn, *args, **kwargs: fn(*args, **kwargs)
    return mock
