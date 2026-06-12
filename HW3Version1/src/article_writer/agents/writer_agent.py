"""WriterAgent and EvaluatorAgent factories — builds the deterministic writing pipeline agents."""
from __future__ import annotations

from crewai import Agent

from article_writer.agents.base_agent import BaseAgentMixin

_WRITER_BACKSTORY = (
    "You are a Senior Technical Article Writer. You transform research material "
    "into well-structured, publication-quality LaTeX articles. You follow writing profiles "
    "exactly, adhere to the given structure, and improve your work iteratively "
    "based on evaluator critique. You never shrink an article below 15 pages."
)

_EVALUATOR_BACKSTORY = (
    "You are a ruthless academic editor. You score articles on 5 dimensions (each 1-10): "
    "coverage (25%), accuracy (25%), style (20%), structure (20%), citation quality (10%). "
    "You produce a structured critique with specific, actionable improvement points. "
    "You always return valid JSON with scores and a critique_points list."
)


def build_writer_agent() -> Agent:
    """Return a configured WriterAgent with skill-enhanced backstory."""
    mixin = BaseAgentMixin()
    backstory = mixin.build_backstory(_WRITER_BACKSTORY, "writing")
    return Agent(
        role="Senior Technical Article Writer",
        goal=(
            "Produce a polished 15-page LaTeX article from research material. "
            "Follow all writing profiles. Compile cleanly with lualatex."
        ),
        backstory=backstory,
        tools=[],
        allow_delegation=True,
        verbose=True,
    )


def build_evaluator_agent() -> Agent:
    """Return a configured EvaluatorAgent (sub-agent delegated from Writer)."""
    return Agent(
        role="Article Quality Evaluator",
        goal=(
            "Score the article draft on 5 dimensions (1-10) and produce actionable "
            "critique in structured JSON format. Minimum 2 iterations required."
        ),
        backstory=_EVALUATOR_BACKSTORY,
        tools=[],
        allow_delegation=False,
        verbose=True,
    )
