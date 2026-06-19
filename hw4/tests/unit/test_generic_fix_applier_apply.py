"""Integration-style tests for GenericFixApplier.apply_from_proposal."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def _applier(results_dir: Path) -> GenericFixApplier:
    llm = MagicMock()
    llm.complete.return_value = (
        f"{_DELIMITER_MODIFIED}\nmodified content\n{_DELIMITER_NEW}\nnew module content"
    )
    return GenericFixApplier(llm, _gatekeeper(), {"results": str(results_dir)})


def _proposal(target_file: str, new_module: str = "new_mod.py") -> dict:
    return {
        "bug": {"bug_type": "HUB", "node_name": "some_node"},
        "target_file": target_file,
        "new_module_name": new_module,
        "change_description": "Extract X into new_mod.py",
        "estimated_degree_reduction": 5,
    }


def test_apply_from_proposal_writes_both_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pkg = repo / "mypkg"
    pkg.mkdir(parents=True)
    (repo / ".git").mkdir()
    target = pkg / "target.py"
    target.write_text("original content")

    proposal = _proposal(str(target), "new_mod.py")
    proposal_file = tmp_path / "results" / "fix_proposal.json"
    proposal_file.parent.mkdir(parents=True)
    proposal_file.write_text(json.dumps(proposal))

    applier = _applier(tmp_path / "results")

    with patch("hw4.shared.git_ops.subprocess.run") as mock_run:
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
    proposal_file = tmp_path / "fix_proposal.json"
    proposal_file.write_text(json.dumps(proposal))

    results_dir = tmp_path / "results"
    results_dir.mkdir()
    applier = _applier(results_dir)

    git_calls = []
    with patch("hw4.shared.git_ops.subprocess.run") as mock_run:
        def capture(*args, **kwargs):
            git_calls.append(args[0])
            return MagicMock(returncode=0, stdout="")
        mock_run.side_effect = capture
        applier.apply_from_proposal(str(proposal_file))

    cmds = [" ".join(c) for c in git_calls]
    assert any("checkout" in c and "-b" in c for c in cmds)
    assert any("add" in c for c in cmds)
    assert any("commit" in c for c in cmds)
