from __future__ import annotations

from unittest.mock import MagicMock

from hw4.models.agent_models import GraphSummary
from hw4.services.functional_bug_detector import PATTERN_CHECKS, FunctionalBugDetectorService


def test_missing_utf8_pattern_detects_buggy_snippet() -> None:
    buggy = '''
def generate_context(context_file, default_context=None, extra_context=None):
    with open(context_file) as file_handle:
        return {}
'''
    assert PATTERN_CHECKS["missing_utf8_open"](buggy) is True


def test_missing_utf8_pattern_passes_fixed_snippet() -> None:
    fixed = '''
def generate_context(context_file, default_context=None, extra_context=None):
    with open(context_file, encoding='utf-8') as file_handle:
        return {}
'''
    assert PATTERN_CHECKS["missing_utf8_open"](fixed) is False


def test_detector_confirms_historical_bug(tmp_path) -> None:
    repo = tmp_path / "cookiecutter"
    pkg = repo / "cookiecutter"
    pkg.mkdir(parents=True)
    (pkg / "generate.py").write_text(
        "def generate_context():\n"
        "    with open(context_file, encoding='utf-8') as file_handle:\n"
        "        pass\n",
        encoding="utf-8",
    )
    gatekeeper = MagicMock()
    gatekeeper.execute.return_value = MagicMock(
        returncode=0,
        stdout=(
            "def generate_context():\n"
            "    with open(context_file) as file_handle:\n"
            "        pass\n"
        ),
    )
    summary = GraphSummary(1, 1, 1, [("generate_generate_files", 14)], 0, "", "")
    bugs = FunctionalBugDetectorService(gatekeeper, "config", str(repo)).detect(summary)
    bug1 = next(b for b in bugs if b.bugsinpy_id == 1)
    assert bug1.status == "CONFIRMED_HISTORICAL"
    assert bug1.graph_hub_match is True
