"""CrewAI Crew wrappers — ArticleResearchCrew and ArticleWritingCrew."""
from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from article_writer.shared.logger import get_logger

logger = get_logger(__name__)


class ArticleResearchCrew:
    """Wraps the sequential research pipeline crew."""

    def __init__(self, researcher: Agent, tasks: list[Task]) -> None:
        self._researcher = researcher
        self._tasks = tasks

    def kickoff(self, inputs: dict) -> str:
        logger.info("ArticleResearchCrew kickoff — inputs: %s", list(inputs.keys()))
        crew = Crew(
            agents=[self._researcher],
            tasks=self._tasks,
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs=inputs)
        logger.info("ArticleResearchCrew complete")
        return str(result)


class ArticleWritingCrew:
    """Wraps the sequential writing + evaluation pipeline crew."""

    def __init__(
        self,
        writer: Agent,
        evaluator: Agent,
        tasks: list[Task],
    ) -> None:
        self._writer = writer
        self._evaluator = evaluator
        self._tasks = tasks

    def kickoff(self, inputs: dict) -> str:
        logger.info("ArticleWritingCrew kickoff — inputs: %s", list(inputs.keys()))
        crew = Crew(
            agents=[self._writer, self._evaluator],
            tasks=self._tasks,
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs=inputs)
        logger.info("ArticleWritingCrew complete")
        return str(result)
