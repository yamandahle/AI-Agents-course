"""CrewAI agent definitions — each agent has a role, goal, backstory, and tools."""

from __future__ import annotations

from crewai import LLM, Agent

from hw4.crewai_tools.tools import (
    load_graph_metrics,
    read_obsidian_files,
    read_source_snippet,
    run_unit_tests,
)
from hw4.shared.provider import ProviderConfig, load_provider


def build_agents(provider: ProviderConfig | None = None) -> dict[str, Agent]:
    """Construct the four CrewAI agents and return them keyed by role slug."""
    if provider is None:
        provider = load_provider()
    llm = LLM(model=provider.model, api_key=provider.api_key, temperature=0.2)

    graph_navigator = Agent(
        role="Graph Navigator",
        goal=(
            "Load the code dependency graph and produce a precise summary of the top "
            "architectural hot-spots: which nodes have the most connections, how many "
            "communities exist, and which files act as bridges between subsystems."
        ),
        backstory=(
            "You are a software architect who specialises in dependency-graph analysis. "
            "You never read entire source files — you navigate the graph first, identify "
            "the most connected nodes, and report exactly what the next agent needs. "
            "Token efficiency is your core discipline."
        ),
        tools=[load_graph_metrics, read_obsidian_files],
        llm=llm,
        verbose=True,
    )

    architect_detective = Agent(
        role="Architect Detective",
        goal=(
            "Classify every node with degree > 10 as a HUB, every node whose removal "
            "increases disconnected components as a SPOF, and every bridge edge as "
            "WEAK_BRIDGE. Rank all bugs by severity and return a structured list."
        ),
        backstory=(
            "You are a forensic software architect. You receive a graph summary and apply "
            "systematic structural rules to detect defects. You output a JSON list of bugs, "
            "each with bug_type, node_name, source_file, severity, and a one-sentence "
            "explanation grounded in the graph data you received."
        ),
        tools=[load_graph_metrics],
        llm=llm,
        verbose=True,
    )

    fix_strategist = Agent(
        role="Fix Strategist",
        goal=(
            "For the highest-severity bug, read the relevant source file snippet and propose "
            "a concrete structural refactor: which file to change, what to extract into a new "
            "module, and why this reduces coupling. If a previous fix attempt failed, address "
            "the failure reason explicitly in the new proposal."
        ),
        backstory=(
            "You are a senior refactoring engineer. You receive a bug list and graph context. "
            "You read only the hot file — never the full repo. You produce one FixProposal "
            "with a target_file, new_module_name, change_description, rationale, and an "
            "estimate of how much the hub degree will drop after the refactor."
        ),
        tools=[read_source_snippet],
        llm=llm,
        verbose=True,
    )

    quality_gate = Agent(
        role="Quality Gate",
        goal=(
            "Run unit tests, check coverage, compare graph metrics before and after the fix. "
            "Return a PASS or FAIL verdict. A FAIL must include a specific retry_instruction "
            "for the Fix Strategist to act on in the next attempt."
        ),
        backstory=(
            "You are a CI/CD quality enforcer. You run tests, check metrics, and deliver "
            "a clear verdict. PASS requires: tests green, coverage >= 85%, and at least "
            "one graph metric improved vs the before-fix baseline. A FAIL verdict includes "
            "exactly what went wrong and what the Fix Strategist must change."
        ),
        tools=[run_unit_tests, load_graph_metrics],
        llm=llm,
        verbose=True,
    )

    return {
        "graph_navigator": graph_navigator,
        "architect_detective": architect_detective,
        "fix_strategist": fix_strategist,
        "quality_gate": quality_gate,
    }
