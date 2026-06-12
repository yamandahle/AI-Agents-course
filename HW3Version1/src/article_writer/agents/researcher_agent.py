"""ResearcherAgent factory — builds the exploratory, human-in-the-loop researcher."""
from __future__ import annotations

from crewai import Agent

from article_writer.agents.base_agent import BaseAgentMixin
from article_writer.shared.config import load_config
from article_writer.tools.citation_extractor import CitationExtractorTool
from article_writer.tools.content_filter import ContentFilterTool
from article_writer.tools.deep_research_tool import DeepResearchTool
from article_writer.tools.researcher_handler import ResearcherHandlerTool

_BASE_BACKSTORY = (
    "You are a meticulous research analyst. You search multiple sources, verify facts, "
    "extract citations, and filter out untrustworthy content. You never skip content "
    "and never keep content below confidence threshold. You follow human feedback "
    "to pivot your research direction after each batch of 5 queries."
)

_ROLE = "Expert Research Analyst"
_GOAL = (
    "Gather comprehensive, verified, cited material on the article topic. "
    "Produce a research.md artifact with at least 10 HIGH/MEDIUM confidence facts "
    "each backed by an inline citation."
)


def build_researcher_agent() -> Agent:
    """Return a configured ResearcherAgent with all 4 tools and skill-enhanced backstory."""
    mixin = BaseAgentMixin()
    backstory = mixin.build_backstory(_BASE_BACKSTORY, "research")
    config = load_config()
    return Agent(
        role=_ROLE,
        goal=_GOAL,
        backstory=backstory,
        tools=[
            DeepResearchTool(),
            ResearcherHandlerTool(),
            CitationExtractorTool(),
            ContentFilterTool(),
        ],
        allow_delegation=False,
        verbose=True,
        max_iter=config.research.max_batches,
    )
