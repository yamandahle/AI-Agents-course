"""Tests for agents/writer_agent.py and crew.py — CrewAI agent factories and crew wrappers."""
from __future__ import annotations

from unittest.mock import MagicMock, patch


def _mock_agent() -> MagicMock:
    return MagicMock()


def _mock_crew(result: str = "crew output") -> MagicMock:
    crew = MagicMock()
    crew.kickoff.return_value = result
    return crew


def test_build_writer_agent_returns_agent() -> None:
    with patch("article_writer.agents.writer_agent.Agent") as MockAgent, \
         patch("article_writer.agents.writer_agent.BaseAgentMixin") as MockMixin:
        MockMixin.return_value.build_backstory.return_value = "backstory"
        from article_writer.agents.writer_agent import build_writer_agent
        build_writer_agent()
    MockAgent.assert_called_once()
    call_kwargs = MockAgent.call_args.kwargs
    assert call_kwargs["role"] == "Senior Technical Article Writer"
    assert call_kwargs["allow_delegation"] is True


def test_build_evaluator_agent_returns_agent() -> None:
    with patch("article_writer.agents.writer_agent.Agent") as MockAgent:
        from article_writer.agents.writer_agent import build_evaluator_agent
        build_evaluator_agent()
    MockAgent.assert_called_once()
    call_kwargs = MockAgent.call_args.kwargs
    assert call_kwargs["role"] == "Article Quality Evaluator"
    assert call_kwargs["allow_delegation"] is False


def test_article_research_crew_kickoff_returns_str() -> None:
    mock_agent = _mock_agent()
    mock_task = MagicMock()
    with patch("article_writer.crew.Crew") as MockCrew:
        MockCrew.return_value.kickoff.return_value = "research done"
        from article_writer.crew import ArticleResearchCrew
        crew = ArticleResearchCrew(researcher=mock_agent, tasks=[mock_task])
        result = crew.kickoff({"topic": "AI"})
    assert result == "research done"
    MockCrew.assert_called_once()


def test_article_writing_crew_kickoff_returns_str() -> None:
    mock_writer = _mock_agent()
    mock_evaluator = _mock_agent()
    mock_task = MagicMock()
    with patch("article_writer.crew.Crew") as MockCrew:
        MockCrew.return_value.kickoff.return_value = "article written"
        from article_writer.crew import ArticleWritingCrew
        crew = ArticleWritingCrew(
            writer=mock_writer, evaluator=mock_evaluator, tasks=[mock_task]
        )
        result = crew.kickoff({"topic": "ML"})
    assert result == "article written"
    MockCrew.assert_called_once()


def test_article_writing_crew_passes_both_agents_to_crew() -> None:
    mock_writer = _mock_agent()
    mock_evaluator = _mock_agent()
    with patch("article_writer.crew.Crew") as MockCrew:
        MockCrew.return_value.kickoff.return_value = "done"
        from article_writer.crew import ArticleWritingCrew
        crew = ArticleWritingCrew(writer=mock_writer, evaluator=mock_evaluator, tasks=[])
        crew.kickoff({})
    agents_passed = MockCrew.call_args.kwargs["agents"]
    assert mock_writer in agents_passed
    assert mock_evaluator in agents_passed
