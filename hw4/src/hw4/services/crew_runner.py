from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crewai import Agent, Crew, Process, Task

from hw4.agents.bug_detector_agent import BugDetectorAgent
from hw4.agents.fix_proposer import FixProposerAgent
from hw4.agents.functional_bug_agent import FunctionalBugAgent
from hw4.agents.graph_reader import GraphReaderAgent
from hw4.agents.verifier import VerifierAgent
from hw4.services.bug_detector import BugDetectorService
from hw4.services.functional_bug_detector import FunctionalBugDetectorService
from hw4.services.graph_builder import GraphBuilderService
from hw4.shared.gatekeeper import ApiGatekeeper
from hw4.shared.llm_client import LlmClient


class CrewRunnerService:
    """Runs the 4-agent pipeline; CrewAI orchestrates, Python does graph work."""

    def __init__(self, gatekeeper: ApiGatekeeper, config: dict, paths: dict) -> None:
        self._gatekeeper = gatekeeper
        self._agents_cfg = config
        self._paths = paths
        self._llm = LlmClient(gatekeeper)

    def run(self) -> dict[str, Any]:
        artifacts = Path(self._paths["artifacts"])
        obsidian = Path(self._paths["obsidian"])
        results = Path(self._paths["results"])
        data = Path(self._paths["data"])
        graph_path = artifacts / "graph.json"
        repo_pkg = data / "cookiecutter" / "cookiecutter"

        graph_builder = GraphBuilderService(self._gatekeeper, self._agents_cfg)
        graph = graph_builder.load_graph(str(graph_path))

        reader = GraphReaderAgent(
            graph_builder,
            str(graph_path),
            str(obsidian),
            max_chars=self._agents_cfg.get("max_prompt_tokens", 2000),
        )
        summary = reader.run()

        detector = BugDetectorService(
            hub_degree_threshold=self._agents_cfg.get("hub_degree_threshold", 10),
        )
        bug_agent = BugDetectorAgent(detector, graph, self._llm)
        bugs = bug_agent.run(summary)

        func_detector = FunctionalBugDetectorService(
            self._gatekeeper,
            repo_root=str(data / "cookiecutter"),
        )
        functional_bugs = FunctionalBugAgent(func_detector).run(summary)

        fix_agent = FixProposerAgent(str(repo_pkg.parent), self._llm)
        proposals = fix_agent.run(bugs, summary)

        verifier = VerifierAgent(str(results / "metrics_before.json"))
        report = verifier.run(summary, len(bugs), proposals)

        token_stats = self._token_comparison(repo_pkg, summary)
        payload = {
            "graph_summary": summary.to_dict(),
            "bugs": [bug.to_dict() for bug in bugs],
            "functional_bugs": [bug.to_dict() for bug in functional_bugs],
            "proposals": [p.to_dict() for p in proposals],
            "verification": report.to_dict(),
            "token_stats": token_stats,
        }
        self._save_results(results, payload)
        self._kickoff_crew(summary, bugs)
        return payload

    def _kickoff_crew(self, summary, bugs) -> None:
        if not self._llm.is_configured():
            return
        analyst = Agent(
            role="Graph Analyst",
            goal="Summarize architectural risks from graph navigation files.",
            backstory="Expert in dependency graphs and reverse engineering.",
            verbose=False,
        )
        task = Task(
            description=(
                f"Nodes={summary.node_count}, hubs={summary.top_hubs[:3]}, "
                f"bugs={[b.node_name for b in bugs[:3]]}. Confirm priorities."
            ),
            expected_output="Short confirmation of top architectural risks.",
            agent=analyst,
        )
        Crew(agents=[analyst], tasks=[task], process=Process.sequential).kickoff()

    def _token_comparison(self, repo_pkg: Path, summary) -> dict[str, int]:
        naive_chars = 0
        if repo_pkg.exists():
            for py_file in repo_pkg.rglob("*.py"):
                naive_chars += len(py_file.read_text(encoding="utf-8", errors="ignore"))
        guided = summary.estimated_tokens
        naive = max(1, naive_chars // 4)
        return {
            "naive_tokens_estimated": naive,
            "graph_guided_tokens_estimated": guided,
            "savings_percent": round(100 * (1 - guided / naive), 1) if naive else 0,
        }

    def _save_results(self, results_dir: Path, payload: dict[str, Any]) -> None:
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "agent_run.json").write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        (results_dir / "bugs.json").write_text(
            json.dumps(payload["bugs"], indent=2),
            encoding="utf-8",
        )
        (results_dir / "functional_bugs.json").write_text(
            json.dumps(payload["functional_bugs"], indent=2),
            encoding="utf-8",
        )
        (results_dir / "fix_proposals.json").write_text(
            json.dumps(payload["proposals"], indent=2),
            encoding="utf-8",
        )
        (results_dir / "token_stats.json").write_text(
            json.dumps(payload["token_stats"], indent=2),
            encoding="utf-8",
        )
