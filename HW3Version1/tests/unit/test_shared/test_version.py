"""Tests for shared/version.py — get_version() reads from config or falls back."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from article_writer.shared.version import get_version


def test_get_version_returns_string() -> None:
    v = get_version()
    assert isinstance(v, str)
    assert len(v) > 0


def test_get_version_format_matches_pattern() -> None:
    v = get_version()
    parts = v.split(".")
    assert len(parts) >= 1
    assert parts[0].isdigit()


def test_get_version_fallback_on_missing_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from article_writer.shared import version as ver_mod
    with patch.object(Path, "read_text", side_effect=FileNotFoundError):
        result = ver_mod.get_version()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_version_reads_from_config(tmp_path: Path, monkeypatch) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "setup.json").write_text(json.dumps({"version": "2.99"}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    from article_writer.shared import version as ver_mod
    import importlib
    importlib.reload(ver_mod)
    result = ver_mod.get_version()
    assert result == "2.99"
