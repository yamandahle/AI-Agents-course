from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hw4.services.graph_builder import GraphBuilderService
from hw4.services.verify_metrics import build_metrics_dict, compare_metrics
from hw4.services.verify_report import render_verification_report
from hw4.shared.gatekeeper import ApiGatekeeper


@dataclass
class VerifyResult:
    metrics_comparison: dict[str, Any]
    tests_passed: bool
    coverage_percent: float
    ruff_clean: bool
    report_path: str


class VerifyService:
    def __init__(
        self,
        gatekeeper: ApiGatekeeper,
        config: dict,
        paths: dict,
        project_root: str = ".",
    ) -> None:
        self._gatekeeper = gatekeeper
        self._config = config
        self._paths = paths
        self._root = Path(project_root)
        self._graph_builder = GraphBuilderService(gatekeeper, config)

    def run(self) -> VerifyResult:
        pkg = self._root / self._paths["data"] / "cookiecutter" / "cookiecutter"
        artifacts = self._root / self._paths["artifacts"]
        results = self._root / self._paths["results"]
        reports = self._root / self._paths["reports"]
        reports.mkdir(parents=True, exist_ok=True)

        self._run_graphify_update(pkg)
        after_dst = artifacts / "graph_after.json"
        after_dst.write_text(
            (pkg / "graphify-out" / "graph.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        before = self._enrich_before(results / "metrics_before.json", artifacts / "graph.json")
        threshold = self._config.get("hub_degree_threshold", 10)
        after_graph = self._graph_builder.load_graph(str(after_dst))
        after = build_metrics_dict(after_graph, self._graph_builder, threshold)
        comparison = compare_metrics(before, after)
        (results / "metrics_after.json").write_text(json.dumps(after, indent=2), encoding="utf-8")
        (results / "metrics_comparison.json").write_text(
            json.dumps(comparison, indent=2),
            encoding="utf-8",
        )

        tests_passed, coverage = self._run_tests()
        ruff_clean = self._run_ruff()
        proposal = self._load_json(results / "fix_proposal.json")
        report_path = reports / "verification.md"
        report_path.write_text(
            render_verification_report(proposal, comparison, tests_passed, coverage, ruff_clean),
            encoding="utf-8",
        )
        return VerifyResult(comparison, tests_passed, coverage, ruff_clean, str(report_path))

    def _enrich_before(self, metrics_path: Path, graph_path: Path) -> dict:
        before = self._load_json(metrics_path)
        if before.get("spof_count") is not None:
            return before
        threshold = self._config.get("hub_degree_threshold", 10)
        graph = self._graph_builder.load_graph(str(graph_path))
        extra = build_metrics_dict(graph, self._graph_builder, threshold)
        before["spof_count"] = extra["spof_count"]
        before["hub_count"] = extra["hub_count"]
        return before

    def _metrics_dict(self, graph) -> dict[str, Any]:
        return build_metrics_dict(
            graph,
            self._graph_builder,
            self._config.get("hub_degree_threshold", 10),
        )

    def _compare(self, before: dict, after: dict) -> dict[str, Any]:
        return compare_metrics(before, after)

    def _run_graphify_update(self, pkg: Path) -> None:
        self._gatekeeper.execute(
            subprocess.run,
            ["graphify", "update", "."],
            cwd=pkg,
            check=True,
        )

    def _run_tests(self) -> tuple[bool, float]:
        result = self._gatekeeper.execute(
            subprocess.run,
            ["uv", "run", "pytest", "tests/unit", "-q", "--cov=src", "--cov-report=term-missing"],
            cwd=self._root,
            capture_output=True,
            text=True,
        )
        coverage = 0.0
        for line in result.stdout.splitlines():
            if line.strip().startswith("TOTAL"):
                coverage = float(line.split()[-1].rstrip("%"))
        return result.returncode == 0, coverage

    def _run_ruff(self) -> bool:
        result = self._gatekeeper.execute(
            subprocess.run,
            ["uv", "run", "ruff", "check", "src", "tests"],
            cwd=self._root,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _load_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
