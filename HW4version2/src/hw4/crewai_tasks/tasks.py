"""CrewAI task definitions — each task declares context= dependencies so agent
outputs flow into the next agent's reasoning automatically."""

from __future__ import annotations

from crewai import Task


def build_tasks(
    agents: dict,
    graph_path: str,
    graph_after_path: str,
    obsidian_dir: str,
    cookiecutter_pkg_dir: str,
    project_root: str = ".",
) -> list[Task]:
    graph_summary_task = Task(
        description=(
            f"1. Call Load Graph Metrics with path='{graph_path}'. "
            f"2. Call Read Obsidian Navigation Files with obsidian_dir='{obsidian_dir}'. "
            "3. Combine both results into a structured summary. "
            "Include: node_count, edge_count, community_count, bridge_count, "
            "top_10_hubs (node_id + degree), and a 2-sentence architectural interpretation."
        ),
        expected_output=(
            "JSON with keys: node_count, edge_count, community_count, bridge_count, "
            "top_10_hubs (list of [node_id, degree]), interpretation (string)."
        ),
        agent=agents["graph_navigator"],
        output_file="results/v2_graph_summary.json",
    )

    bug_detection_task = Task(
        description=(
            "You received a graph summary from the Graph Navigator. "
            "Apply these rules to detect bugs: "
            "(A) HUB — any node with degree > 10; severity HIGH if degree > 15, else MEDIUM. "
            "(B) SPOF — any node in the top-15 by degree whose removal would disconnect the graph. "
            "(C) WEAK_BRIDGE — any bridge edge connecting otherwise separate communities. "
            "Return a JSON list ranked HIGH first, max 5 bugs."
        ),
        expected_output=(
            "JSON list where each item has: bug_type, node_name, source_file, "
            "severity (HIGH|MEDIUM|LOW), explanation (one sentence, citing the degree or "
            "connectivity evidence from the graph summary)."
        ),
        agent=agents["architect_detective"],
        context=[graph_summary_task],
        output_file="results/v2_bugs.json",
    )

    fix_proposal_task = Task(
        description=(
            "You received the bug list. Pick the top-severity HUB bug. "
            f"Read its source file from '{cookiecutter_pkg_dir}/' using Read Source File Snippet. "
            "Then propose a concrete refactor: "
            "— which file to change (target_file) "
            "— what new module to create (new_module_name) "
            "— what logic to move into it (change_description) "
            "— why this reduces coupling (rationale) "
            "— estimate how much the hub degree will drop (estimated_degree_reduction). "
            "If the task context includes a previous FAIL verdict, address the "
            "retry_instruction from that verdict explicitly."
        ),
        expected_output=(
            "JSON with: bug (the chosen ArchitecturalBug object), target_file, "
            "new_module_name, change_description, rationale, estimated_degree_reduction (int)."
        ),
        agent=agents["fix_strategist"],
        context=[graph_summary_task, bug_detection_task],
        output_file="results/v2_fix_proposal.json",
    )

    verification_task = Task(
        description=(
            f"You received the fix proposal. "
            f"1. Run unit tests with project_root='{project_root}' using Run Unit Tests. "
            f"2. Call Load Graph Metrics on '{graph_after_path}' (the post-fix graph). "
            "3. Compare node_count, edge_count, community_count to the before values "
            "   in the graph summary from the Graph Navigator. "
            "4. Produce a verdict: PASS if tests green AND coverage >= 85% AND "
            "   at least one metric improved. Otherwise FAIL. "
            "5. For a FAIL, write a specific retry_instruction telling the Fix Strategist "
            "   exactly what to change (e.g. 'move X to Y instead of Z')."
        ),
        expected_output=(
            "JSON with: verdict (PASS|FAIL), tests_passed (bool), coverage_percent (float), "
            "metrics_improved (bool), metrics_delta (dict of before/after values), "
            "failure_reason (str or null), retry_instruction (str or null)."
        ),
        agent=agents["quality_gate"],
        context=[bug_detection_task, fix_proposal_task],
        output_file="results/v2_verification.json",
    )

    return [graph_summary_task, bug_detection_task, fix_proposal_task, verification_task]
