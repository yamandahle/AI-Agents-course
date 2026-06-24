"""T747–T760: Submission structure and project integrity checks."""

from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path

import pytest

HW5_ROOT = Path(__file__).parents[2]
SRC_DIR = HW5_ROOT / "src"
CONFIG_DIR = HW5_ROOT / "config"
DOCS_DIR = HW5_ROOT / "docs"

# ── T747: prompts_ive_used.md exists and is non-empty ────────────────────────


def test_prompts_file_exists_and_is_non_empty():
    p = HW5_ROOT / "prompts_ive_used.md"
    assert p.exists(), "prompts_ive_used.md must exist"
    assert p.stat().st_size > 0, "prompts_ive_used.md must not be empty"


# ── T748: docs/PRD.md has "Acceptance Criteria" ──────────────────────────────


def test_prd_contains_acceptance_criteria():
    p = DOCS_DIR / "PRD.md"
    assert p.exists(), "docs/PRD.md must exist"
    assert "Acceptance Criteria" in p.read_text()


# ── T749: config/models.json is valid JSON ────────────────────────────────────


def test_models_json_is_valid_json():
    p = CONFIG_DIR / "models.json"
    assert p.exists(), "config/models.json must exist"
    data = json.loads(p.read_text())
    assert "models" in data


# ── T750: config/setup.json is valid JSON ────────────────────────────────────


def test_setup_json_is_valid_json():
    p = CONFIG_DIR / "setup.json"
    assert p.exists(), "config/setup.json must exist"
    data = json.loads(p.read_text())
    assert "frameworks" in data


# ── T751: config/rate_limits.json is valid JSON ───────────────────────────────


def test_rate_limits_json_is_valid_json():
    p = CONFIG_DIR / "rate_limits.json"
    assert p.exists(), "config/rate_limits.json must exist"
    json.loads(p.read_text())  # raises on invalid JSON


# ── T752: required project directories exist ──────────────────────────────────


@pytest.mark.parametrize("name", ["data", "results", "assets", "notebooks"])
def test_required_directory_exists(name: str):
    d = HW5_ROOT / name
    assert d.exists() and d.is_dir(), f"Directory {name}/ must exist"


# ── T753: .env file does not exist ────────────────────────────────────────────


def test_env_file_does_not_exist():
    assert not (HW5_ROOT / ".env").exists(), ".env must not be committed"


# ── T756: uv.lock exists and is non-empty ─────────────────────────────────────


def test_uv_lock_exists_and_is_non_empty():
    p = HW5_ROOT / "uv.lock"
    assert p.exists(), "uv.lock must exist"
    assert p.stat().st_size > 0, "uv.lock must not be empty"


# ── T757: pyproject.toml has [tool.ruff] ─────────────────────────────────────


def test_pyproject_has_ruff_section():
    p = HW5_ROOT / "pyproject.toml"
    assert p.exists(), "pyproject.toml must exist"
    content = p.read_text()
    assert "[tool.ruff]" in content


# ── T758: pyproject.toml has [tool.pytest.ini_options] ───────────────────────


def test_pyproject_has_pytest_section():
    content = (HW5_ROOT / "pyproject.toml").read_text()
    assert "[tool.pytest.ini_options]" in content


# ── T759: no src/ file has spaces or non-ASCII in its name ───────────────────


def test_no_src_file_has_spaces_or_non_ascii():
    bad = [
        p
        for p in SRC_DIR.rglob("*.py")
        if " " in p.name or not p.name.isascii()
    ]
    assert not bad, f"Files with invalid names: {bad}"


# ── T760: all hw5 modules import without circular imports ────────────────────


def test_all_hw5_modules_import_cleanly():
    import hw5

    failed: list[str] = []
    for importer, modname, _ in pkgutil.walk_packages(
        path=hw5.__path__,  # type: ignore[attr-defined]
        prefix=hw5.__name__ + ".",
        onerror=lambda n: None,
    ):
        try:
            importlib.import_module(modname)
        except Exception as exc:
            failed.append(f"{modname}: {exc}")

    assert not failed, "Import failures:\n" + "\n".join(failed)
