"""Unit tests for shared/git_ops.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from hw4.shared.git_ops import branch_name, export_diff, find_git_root


def _gatekeeper() -> ApiGatekeeper:
    cfg = RateLimitConfig(60, 1000, 5, 0, 1)
    gk = ApiGatekeeper(config=cfg)
    gk.execute = lambda fn, *a, **kw: fn(*a, **kw)
    return gk


# ── find_git_root ─────────────────────────────────────────────────────────────

def test_find_git_root_finds_dotgit(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "pkg" / "sub"
    nested.mkdir(parents=True)
    target_file = nested / "myfile.py"
    target_file.write_text("x = 1")
    assert find_git_root(target_file) == tmp_path


def test_find_git_root_raises_when_no_git(tmp_path: Path) -> None:
    target_file = tmp_path / "myfile.py"
    target_file.write_text("x = 1")
    with pytest.raises(FileNotFoundError, match="No .git directory"):
        find_git_root(target_file)


# ── branch_name ───────────────────────────────────────────────────────────────

def test_branch_name_slugifies_node() -> None:
    proposal = {"bug": {"bug_type": "HUB", "node_name": "Some_Module.Class"}}
    assert branch_name(proposal) == "fix/hub-some-module-class"


def test_branch_name_truncates_long_node() -> None:
    proposal = {"bug": {"bug_type": "SPOF", "node_name": "a" * 60}}
    br = branch_name(proposal)
    assert len(br) <= len("fix/spof-") + 40


def test_branch_name_defaults_on_missing_bug() -> None:
    br = branch_name({})
    assert br.startswith("fix/fix-")


# ── export_diff ───────────────────────────────────────────────────────────────

def test_export_diff_writes_patch(tmp_path: Path) -> None:
    gk = _gatekeeper()
    fake_result = MagicMock()
    fake_result.stdout = "diff output"

    called = []

    def fake_execute(fn, *args, **kwargs):
        called.append(args[0])
        return fake_result

    gk.execute = fake_execute
    patch_path = export_diff(tmp_path, tmp_path, gk)
    assert patch_path == tmp_path / "fix_diff.patch"
    assert patch_path.read_text() == "diff output"


def test_export_diff_handles_empty_stdout(tmp_path: Path) -> None:
    gk = _gatekeeper()
    fake_result = MagicMock()
    fake_result.stdout = None
    gk.execute = lambda fn, *a, **kw: fake_result
    patch_path = export_diff(tmp_path, tmp_path, gk)
    assert patch_path.read_text() == ""
