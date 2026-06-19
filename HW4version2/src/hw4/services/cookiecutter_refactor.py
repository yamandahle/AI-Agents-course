"""Apply cookiecutter main.py hub refactor from packaged templates."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def _load_template(filename: str) -> str:
    return (files("hw4.resources") / filename).read_text(encoding="utf-8")


def apply_main_hub_refactor(repo_root: Path) -> bool:
    """Extract orchestration from main.py; return True if files were written."""
    main_path = repo_root / "cookiecutter" / "main.py"
    orch_path = repo_root / "cookiecutter" / "orchestration.py"
    if "orchestration" in main_path.read_text(encoding="utf-8"):
        return False
    orch_path.write_text(_load_template("cookiecutter_orchestration.txt"), encoding="utf-8")
    main_path.write_text(_load_template("cookiecutter_main.txt"), encoding="utf-8")
    return True
