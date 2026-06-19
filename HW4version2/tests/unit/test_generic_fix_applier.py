"""Unit tests for services/generic_fix_applier.py."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hw4.services.generic_fix_applier import (
    _DELIMITER_MODIFIED,
    _DELIMITER_NEW,
    GenericFixApplier,
)
from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig


def _gatekeeper() -> ApiGatekeeper:
    cfg = RateLimitConfig(60, 1000, 5, 0, 1)
    gk = ApiGatekeeper(config=cfg)
    gk.execute = lambda fn, *a, **kw: fn(*a, **kw)
    return gk


def _applier(tmp_path: Path) -> GenericFixApplier:
    llm = MagicMock()
    llm.complete.return_value = (
        f"{_DELIMITER_MODIFIED}\nmodified content\n{_DELIMITER_NEW}\nnew module content"
    )
    return GenericFixApplier(llm, _gatekeeper(), {"results": str(tmp_path)})


def _proposal(target_file: str, new_module: str = "new_mod.py") -> dict:
    return {
        "bug": {"bug_type": "HUB", "node_name": "some_node"},
        "target_file": target_file,
        "new_module_name": new_module,
        "change_description": "Extract X into new_mod.py",
        "estimated_degree_reduction": 5,
    }


# ── _parse_response ───────────────────────────────────────────────────────────

def test_parse_response_valid(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    response = f"{_DELIMITER_MODIFIED}\nAAA\n{_DELIMITER_NEW}\nBBB"
    modified, new_mod = applier._parse_response(response)
    assert modified == "AAA"
    assert new_mod == "BBB"


def test_parse_response_missing_modified_raises(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    with pytest.raises(ValueError, match="missing required delimiters"):
        applier._parse_response(f"some text\n{_DELIMITER_NEW}\nBBB")


def test_parse_response_missing_new_raises(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    with pytest.raises(ValueError, match="missing required delimiters"):
        applier._parse_response(f"{_DELIMITER_MODIFIED}\nAAA")


def test_parse_response_strips_whitespace(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    response = f"{_DELIMITER_MODIFIED}\n  AAA  \n{_DELIMITER_NEW}\n  BBB  "
    modified, new_mod = applier._parse_response(response)
    assert modified == "AAA"
    assert new_mod == "BBB"


# ── _find_git_root ────────────────────────────────────────────────────────────

def test_find_git_root_finds_dotgit(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "pkg" / "sub"
    nested.mkdir(parents=True)
    target_file = nested / "myfile.py"
    target_file.write_text("x = 1")

    applier = _applier(tmp_path)
    assert applier._find_git_root(target_file) == tmp_path


def test_find_git_root_raises_when_no_git(tmp_path: Path) -> None:
    target_file = tmp_path / "myfile.py"
    target_file.write_text("x = 1")
    applier = _applier(tmp_path)
    with pytest.raises(FileNotFoundError, match="No .git directory"):
        applier._find_git_root(target_file)


# ── _branch_name ─────────────────────────────────────────────────────────────

def test_branch_name_slugifies_node(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    proposal = {"bug": {"bug_type": "HUB", "node_name": "Some_Module.Class"}}
    assert applier._branch_name(proposal) == "fix/hub-some-module-class"


def test_branch_name_truncates_long_node(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    proposal = {"bug": {"bug_type": "SPOF", "node_name": "a" * 60}}
    branch = applier._branch_name(proposal)
    assert len(branch) <= len("fix/spof-") + 40


def test_branch_name_defaults_on_missing_bug(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    branch = applier._branch_name({})
    assert branch.startswith("fix/fix-")


# ── apply_from_proposal — full mock ──────────────────────────────────────────

def test_apply_from_proposal_writes_both_files(tmp_path: Path) -> None:
    # Set up a fake git repo
    repo = tmp_path / "repo"
    pkg = repo / "mypkg"
    pkg.mkdir(parents=True)
    (repo / ".git").mkdir()
    target = pkg / "target.py"
    target.write_text("original content")

    proposal = _proposal(str(target), "new_mod.py")
    proposal_file = tmp_path / "results" / "v2_fix_proposal.json"
    proposal_file.parent.mkdir(parents=True)
    proposal_file.write_text(json.dumps(proposal))

    applier = _applier(tmp_path / "results")
    applier._results = tmp_path / "results"

    with patch("hw4.services.generic_fix_applier.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="diff output")
        result = applier.apply_from_proposal(str(proposal_file))

    assert target.read_text() == "modified content"
    assert (pkg / "new_mod.py").read_text() == "new module content"
    assert result.committed is True
    assert result.branch == "fix/hub-some-node"


def test_apply_from_proposal_commits_correct_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pkg = repo / "mypkg"
    pkg.mkdir(parents=True)
    (repo / ".git").mkdir()
    target = pkg / "target.py"
    target.write_text("code")

    proposal = _proposal(str(target), "extracted.py")
    proposal_file = tmp_path / "v2_fix_proposal.json"
    proposal_file.write_text(json.dumps(proposal))

    results_dir = tmp_path / "results"
    results_dir.mkdir()
    applier = _applier(results_dir)
    applier._results = results_dir

    git_calls = []
    with patch("hw4.services.generic_fix_applier.subprocess.run") as mock_run:
        def capture(*args, **kwargs):
            git_calls.append(args[0])
            return MagicMock(returncode=0, stdout="")
        mock_run.side_effect = capture
        applier.apply_from_proposal(str(proposal_file))

    cmds = [" ".join(c) for c in git_calls]
    assert any("checkout" in c and "-b" in c for c in cmds)
    assert any("add" in c for c in cmds)
    assert any("commit" in c for c in cmds)
