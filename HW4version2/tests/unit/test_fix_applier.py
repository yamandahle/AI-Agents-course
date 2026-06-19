from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.services.cookiecutter_refactor import apply_main_hub_refactor
from hw4.services.fix_applier import FixApplierService


@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    data_dir = tmp_path
    repo_root = data_dir / "cookiecutter"
    pkg = repo_root / "cookiecutter"
    pkg.mkdir(parents=True)
    (pkg / "main.py").write_text(
        "def cookiecutter():\n    pass\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return data_dir


def test_apply_main_hub_refactor_creates_orchestration(mini_repo: Path) -> None:
    repo_root = mini_repo / "cookiecutter"
    changed = apply_main_hub_refactor(repo_root)
    assert changed is True
    assert (repo_root / "cookiecutter" / "orchestration.py").exists()
    main_text = (repo_root / "cookiecutter" / "main.py").read_text(encoding="utf-8")
    assert "orchestration" in main_text


def test_fix_applier_writes_patch(tmp_path: Path, mini_repo: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    proposals = [
        {
            "bug": {
                "bug_type": "HUB",
                "node_name": "cookiecutter()",
                "severity": "HIGH",
                "explanation": "hub",
                "source_file": "main.py",
            },
            "target_file": "main.py",
            "change_description": "split",
            "rationale": "reduce coupling",
        }
    ]
    (results / "fix_proposals.json").write_text(json.dumps(proposals), encoding="utf-8")
    paths = {"results": f"{results}/", "data": f"{mini_repo}/"}
    gatekeeper = MagicMock()
    gatekeeper.execute.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="diff --git a/cookiecutter/main.py\n"
    )
    result = FixApplierService(gatekeeper, paths).apply_from_file()
    assert result.committed is True
    assert Path(result.patch_path).exists()
    assert (results / "fix_proposal.json").exists()
