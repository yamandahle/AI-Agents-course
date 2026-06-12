"""Research task factories — defines the 3-task research pipeline."""
from __future__ import annotations

from crewai import Agent, Task


def make_research_batch_task(researcher: Agent, topic: str) -> Task:
    """Batch search task — pauses for human feedback after execution."""
    return Task(
        description=(
            f"Research the topic: '{topic}'.\n"
            "1. Use researcher_handler to plan 5 search queries.\n"
            "2. For each query: call deep_research with the exact query as prompt.\n"
            "3. For each returned source: call citation_extractor.\n"
            "4. For each content chunk: call content_filter with 'content | Topic: {topic}'.\n"
            "5. Present results and wait for human feedback.\n"
            "Do NOT run more than 5 queries before pausing."
        ),
        expected_output=(
            "A markdown list of facts with inline [source](url) citations. "
            "Each fact tagged with confidence: HIGH or MEDIUM. LOW items excluded."
        ),
        agent=researcher,
        human_input=True,
    )


def make_research_filter_task(researcher: Agent, batch_task: Task) -> Task:
    """Filter task — removes duplicates and LOW confidence items from batch results."""
    return Task(
        description=(
            "Review all content gathered in the previous batch.\n"
            "1. Remove any duplicate facts.\n"
            "2. Remove any LOW confidence items.\n"
            "3. Keep only HIGH and MEDIUM confidence facts.\n"
            "4. Ensure every kept fact has an inline citation."
        ),
        expected_output=(
            "A cleaned, deduplicated list of HIGH and MEDIUM confidence facts with citations."
        ),
        agent=researcher,
        context=[batch_task],
    )


def make_research_artifact_task(researcher: Agent, filter_task: Task) -> Task:
    """Artifact task — writes curated research to data/research.md."""
    return Task(
        description=(
            "Write all curated facts to data/research.md.\n"
            "Format:\n"
            "  # Research: {topic}\n"
            "  ## <DimensionName>\n"
            "  - **Fact**: ... — **Confidence**: HIGH — **Source**: [title](url)\n"
            "Include a ## Raw Sources section at the end listing all cited URLs."
        ),
        expected_output="Path to completed data/research.md with ≥10 cited facts.",
        agent=researcher,
        context=[filter_task],
    )
