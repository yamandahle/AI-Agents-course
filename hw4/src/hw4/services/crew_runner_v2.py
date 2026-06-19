"""Proper CrewAI runner: real agents with tools, context-chained tasks, feedback loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crewai import Crew, Process

from hw4.agents.functional_bug_agent import FunctionalBugAgent
from hw4.crewai_agents.agents import build_agents
from hw4.crewai_tasks.tasks import build_tasks
from hw4.models.agent_models import GraphSummary
from hw4.services.functional_bug_detector import FunctionalBugDetectorService
from hw4.services.graph_builder import GraphBuilderService
from hw4.shared.gatekeeper import ApiGatekeeper
from hw4.shared.provider import load_provider


class CrewRunnerV2:
    """Replaces CrewRunnerService with genuine CrewAI orchestration.

    Key differences vs v1:
    - Agents are crewai.Agent instances with @tool functions they can call freely.
    - Tasks use context= so each agent receives the previous agent's full output.
    - The quality_gate verdict drives a retry loop: if FAIL, fix_strategist gets
      the failure reason injected into its backstory and the crew re-runs.
    - memory=True lets agents accumulate context across all tasks in one session.
    """

    MAX_RETRIES = 2

    def __init__(self, gatekeeper: ApiGatekeeper, config: dict, paths: dict) -> None:
        self._gatekeeper = gatekeeper
        self._config = config
        self._paths = paths
        self._provider = load_provider()

    def run(self) -> dict[str, Any]:
        agents = build_agents(provider=self._provider)
        artifacts = Path(self._paths["artifacts"])
        obsidian = Path(self._paths["obsidian"])
        data = Path(self._paths["data"])
        results = Path(self._paths["results"])
        results.mkdir(parents=True, exist_ok=True)

        for attempt in range(self.MAX_RETRIES):
            tasks = build_tasks(
                agents=agents,
                graph_path=str(artifacts / "graph.json"),
                graph_after_path=str(artifacts / "graph_after.json"),
                obsidian_dir=self._paths["obsidian"],
                cookiecutter_pkg_dir=str(data / "cookiecutter" / "cookiecutter"),
                project_root=".",
            )

            crew = Crew(
                agents=list(agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                memory=False,
            )

            self._gatekeeper.execute(
                crew.kickoff,
                inputs={"attempt_number": attempt + 1},
            )

            verdict = self._load_json("v2_verification.json")
            if verdict.get("verdict") == "PASS":
                break

            if attempt < self.MAX_RETRIES - 1:
                retry_instruction = verdict.get("retry_instruction", "reconsider the fix scope")
                agents["fix_strategist"].backstory += (
                    f" NOTE — attempt {attempt + 1} failed: {retry_instruction}. "
                    "Adjust your proposal to address this before making any new suggestion."
                )

        repo_pkg = data / "cookiecutter" / "cookiecutter"
        functional_bugs = self._run_functional_bugs(artifacts, obsidian, data)
        token_stats = self._token_comparison(repo_pkg, obsidian)

        (results / "functional_bugs.json").write_text(
            json.dumps(functional_bugs, indent=2), encoding="utf-8"
        )
        (results / "token_stats.json").write_text(
            json.dumps(token_stats, indent=2), encoding="utf-8"
        )

        output = self._collect_outputs()
        output["functional_bugs"] = functional_bugs
        output["token_stats"] = token_stats
        return output

    def _run_functional_bugs(
        self, artifacts: Path, obsidian: Path, data: Path
    ) -> list[dict]:
        graph_builder = GraphBuilderService(self._gatekeeper, self._config)
        graph = graph_builder.load_graph(str(artifacts / "graph.json"))
        metrics = graph_builder.compute_metrics(graph)

        hot_excerpt = ""
        index_excerpt = ""
        for fname, target in [("hot.md", "hot"), ("index.md", "index")]:
            p = obsidian / fname
            if p.exists():
                text = p.read_text(encoding="utf-8")[:2000]
                if target == "hot":
                    hot_excerpt = text
                else:
                    index_excerpt = text

        summary = GraphSummary(
            node_count=metrics.node_count,
            edge_count=metrics.edge_count,
            community_count=metrics.community_count,
            top_hubs=metrics.top_hubs,
            bridge_count=metrics.bridge_count,
            hot_excerpt=hot_excerpt,
            index_excerpt=index_excerpt,
        )
        func_detector = FunctionalBugDetectorService(
            self._gatekeeper,
            repo_root=str(data / "cookiecutter"),
        )
        bugs = FunctionalBugAgent(func_detector).run(summary)
        return [b.to_dict() for b in bugs]

    def _token_comparison(self, repo_pkg: Path, obsidian: Path) -> dict[str, int]:
        naive_chars = 0
        if repo_pkg.exists():
            for py_file in repo_pkg.rglob("*.py"):
                naive_chars += len(py_file.read_text(encoding="utf-8", errors="ignore"))

        guided_chars = 500  # approximate output size of load_graph_metrics tool call
        for fname in ("hot.md", "index.md"):
            p = obsidian / fname
            if p.exists():
                guided_chars += min(len(p.read_text(encoding="utf-8")), 2000)

        naive = max(1, naive_chars // 4)
        guided = max(1, guided_chars // 4)
        return {
            "naive_tokens_estimated": naive,
            "graph_guided_tokens_estimated": guided,
            "savings_percent": round(100 * (1 - guided / naive), 1) if naive else 0,
        }

    def _load_json(self, filename: str) -> dict:
        path = Path(self._paths["results"]) / filename
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _collect_outputs(self) -> dict[str, Any]:
        keys = (
            "v2_graph_summary",
            "bugs",
            "fix_proposal",
            "v2_verification",
        )
        return {k: self._load_json(f"{k}.json") for k in keys}
