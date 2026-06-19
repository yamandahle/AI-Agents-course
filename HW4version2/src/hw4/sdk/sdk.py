from __future__ import annotations

from pathlib import Path
from typing import Any

from hw4.services.bug_detector import BugDetectorService
from hw4.services.crew_runner import CrewRunnerService
from hw4.services.generic_fix_applier import FixResult, GenericFixApplier
from hw4.services.graph_builder import GraphBuilderService
from hw4.services.verify_service import VerifyResult, VerifyService
from hw4.shared.config import ConfigManager
from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from hw4.shared.llm_client import LlmClient
from hw4.shared.provider import load_provider


class HW4SDK:
    """Public entry point for the EX04 pipeline — all pipeline logic flows through here."""

    def __init__(self, config_dir: str = "config") -> None:
        self.config = ConfigManager(config_dir)
        self.gatekeeper = self._build_gatekeeper()
        self.graph_builder = GraphBuilderService(
            self.gatekeeper,
            self.config.get("agents"),
        )

    def _build_gatekeeper(self) -> ApiGatekeeper:
        limits = self.config.get_rate_limit(load_provider().rate_limit_key)
        return ApiGatekeeper(
            config=RateLimitConfig(
                requests_per_minute=limits["requests_per_minute"],
                requests_per_hour=limits["requests_per_hour"],
                concurrent_max=limits["concurrent_max"],
                retry_after_seconds=limits["retry_after_seconds"],
                max_retries=limits["max_retries"],
            )
        )

    def run_grphify(self, backend: str = "claude", project_root: str = ".") -> None:
        """Run the Grphify static analysis pass and sync deliverables to artifacts/."""
        root = Path(project_root)
        paths = self.config.get("paths")
        artifacts = root / paths["artifacts"]
        package = self.graph_builder.package_dir(root, paths)
        graphify_out = self.graph_builder.run_grphify(package, artifacts, backend=backend)
        self.graph_builder.sync_deliverables(graphify_out, artifacts)

    def run_agents(self) -> dict[str, Any]:
        """Run the four CrewAI agents in sequence and return their combined outputs."""
        runner = CrewRunnerService(
            self.gatekeeper,
            self.config.get("agents"),
            self.config.get("paths"),
        )
        return runner.run()

    def detect_bugs(self) -> list[dict]:
        """Detect architectural bugs in the current graph and return a ranked list."""
        graph_path = self.config.get("paths", "artifacts") + "graph.json"
        graph = self.graph_builder.load_graph(graph_path)
        summary_metrics = self.graph_builder.compute_metrics(graph)
        from hw4.models.agent_models import GraphSummary

        summary = GraphSummary(
            node_count=summary_metrics.node_count,
            edge_count=summary_metrics.edge_count,
            community_count=summary_metrics.community_count,
            top_hubs=summary_metrics.top_hubs,
            bridge_count=summary_metrics.bridge_count,
            hot_excerpt="",
            index_excerpt="",
        )
        detector = BugDetectorService(
            hub_degree_threshold=self.config.get("agents", "hub_degree_threshold"),
        )
        bugs = detector.detect(graph, summary)
        return [bug.to_dict() for bug in bugs]

    def apply_fix(self) -> FixResult:
        """Apply the LLM-generated fix from v2_fix_proposal.json and commit the result."""
        llm = LlmClient(self.gatekeeper)
        applier = GenericFixApplier(llm, self.gatekeeper, self.config.get("paths"))
        return applier.apply_from_proposal()

    def verify(self) -> VerifyResult:
        """Re-scan the graph, run pytest, and produce the verification report."""
        return VerifyService(
            self.gatekeeper,
            self.config.get("agents"),
            self.config.get("paths"),
        ).run()
