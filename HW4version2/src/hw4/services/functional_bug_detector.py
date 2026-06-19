from __future__ import annotations

import json
import subprocess
import urllib.request
from collections.abc import Callable
from pathlib import Path

from hw4.models.agent_models import FunctionalBug, GraphSummary
from hw4.shared.gatekeeper import ApiGatekeeper

PatternCheck = Callable[[str], bool]


def _chunk(text: str, func_name: str) -> str:
    marker = f"def {func_name}"
    if marker not in text:
        return ""
    body = text.split(marker, 1)[1]
    return body.split("\ndef ", 1)[0]


PATTERN_CHECKS: dict[str, PatternCheck] = {
    "missing_utf8_open": lambda text: _chunk(text, "generate_context")
    and "open(context_file)" in _chunk(text, "generate_context")
    and "encoding=" not in _chunk(text, "generate_context"),
    "single_hook_return": lambda text: (
        "def find_hook" in text
        and "return os.path.abspath" in text
        and "scripts.append" not in text
    ),
    "missing_show_choices_false": lambda text: (
        "def read_user_choice" in text
        and "click.prompt" in text
        and "show_choices=False" not in text
    ),
    "missing_failed_hook_exception": lambda text: "class FailedHookException" not in text,
}


class FunctionalBugDetectorService:
    """Detect BugsInPy-style functional bugs on graph-hot files."""

    def __init__(
        self,
        gatekeeper: ApiGatekeeper,
        config_dir: str = "config",
        repo_root: str | None = None,
    ) -> None:
        self._gatekeeper = gatekeeper
        self._repo_root = Path(repo_root) if repo_root else None
        catalog_path = Path(config_dir) / "bugsinpy_cookiecutter.json"
        self._catalog = json.loads(catalog_path.read_text(encoding="utf-8"))["bugs"]

    def detect(self, summary: GraphSummary) -> list[FunctionalBug]:
        hot_files = self._hot_files(summary)
        bugs: list[FunctionalBug] = []
        for entry in self._catalog:
            rel_path = entry["file"].replace("cookiecutter/", "")
            graph_match = rel_path in hot_files or entry["file"] in hot_files
            if not graph_match:
                continue
            bugs.append(self._inspect_entry(entry, graph_match))
        return bugs

    def _inspect_entry(self, entry: dict, graph_match: bool) -> FunctionalBug:
        check = PATTERN_CHECKS[entry["check"]]
        current = self._read_current(entry["file"])
        buggy = self._read_commit(entry["buggy_commit"], entry["file"])
        buggy_hit = check(buggy) if buggy else False
        current_hit = check(current) if current else False
        if current_hit:
            status = "OPEN"
        elif buggy_hit:
            status = "CONFIRMED_HISTORICAL"
        else:
            status = "NOT_DETECTED"
        return FunctionalBug(
            bugsinpy_id=entry["id"],
            source_file=entry["file"],
            description=entry["description"],
            severity="HIGH" if current_hit else "MEDIUM",
            status=status,
            graph_hub_match=graph_match,
            buggy_commit=entry["buggy_commit"],
            test_file=entry["test_file"],
        )

    def _hot_files(self, summary: GraphSummary) -> set[str]:
        names: set[str] = set()
        for node, _ in summary.top_hubs[:10]:
            for part in (node, summary.hot_excerpt, summary.index_excerpt):
                if "generate" in part:
                    names.add("generate.py")
                if "prompt" in part:
                    names.add("prompt.py")
                if "hooks" in part:
                    names.add("hooks.py")
                if "exceptions" in part:
                    names.add("exceptions.py")
                if "main" in part:
                    names.add("main.py")
        names.update({"generate.py", "prompt.py", "hooks.py", "exceptions.py"})
        return names

    def _read_current(self, repo_path: str) -> str:
        if not self._repo_root:
            return ""
        path = self._repo_root / repo_path
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _read_commit(self, commit: str, repo_path: str) -> str:
        if self._repo_root:
            result = self._gatekeeper.execute(
                subprocess.run,
                ["git", "show", f"{commit}:{repo_path}"],
                cwd=self._repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout
        return self._fetch_github(commit, repo_path)

    def _fetch_github(self, commit: str, repo_path: str) -> str:
        url = f"https://raw.githubusercontent.com/cookiecutter/cookiecutter/{commit}/{repo_path}"

        def _get() -> str:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read().decode("utf-8")

        try:
            return self._gatekeeper.execute(_get)
        except Exception:
            return ""
