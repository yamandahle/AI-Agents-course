from __future__ import annotations

from hw4.models.agent_models import FunctionalBug, GraphSummary
from hw4.services.functional_bug_detector import FunctionalBugDetectorService


class FunctionalBugAgent:
    """Agent 5: graph-guided scan for BugsInPy-style functional defects."""

    def __init__(self, detector: FunctionalBugDetectorService) -> None:
        self._detector = detector

    def run(self, summary: GraphSummary) -> list[FunctionalBug]:
        return self._detector.detect(summary)
