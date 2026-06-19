"""Proper CrewAI runner: real agents with tools, context-chained tasks, feedback loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crewai import Crew, Process

from hw4.crewai_agents.agents import build_agents
from hw4.crewai_tasks.tasks import build_tasks
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
        """Kick off the CrewAI crew with retry logic and return collected agent outputs."""
        agents = build_agents(provider=self._provider)
        artifacts = Path(self._paths["artifacts"])
        data = Path(self._paths["data"])

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

        return self._collect_outputs()

    def _load_json(self, filename: str) -> dict:
        path = Path(self._paths["results"]) / filename
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _collect_outputs(self) -> dict[str, Any]:
        keys = ("v2_graph_summary", "v2_bugs", "v2_fix_proposal", "v2_verification")
        return {k: self._load_json(f"{k}.json") for k in keys}
