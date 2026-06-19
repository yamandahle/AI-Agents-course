from __future__ import annotations

import json
from pathlib import Path

from hw4.models.agent_models import FixProposal, GraphSummary, VerificationReport


class VerifierAgent:
    """Agent 4: validates agent outputs and compares metrics baseline."""

    def __init__(self, metrics_before_path: str) -> None:
        self._metrics_path = Path(metrics_before_path)

    def run(
        self,
        summary: GraphSummary,
        bugs_count: int,
        proposals: list[FixProposal],
    ) -> VerificationReport:
        """Compare current metrics against the baseline and return a VerificationReport."""
        baseline = self._load_baseline()
        delta = 0.0
        if baseline:
            before_hubs = baseline.get("top_hubs", [[None, 0]])[0][1]
            after_hubs = summary.top_hubs[0][1] if summary.top_hubs else 0
            if before_hubs:
                delta = (after_hubs - before_hubs) / before_hubs

        ok = bugs_count > 0 and len(proposals) > 0
        return VerificationReport(
            fix_applied=False,
            tests_passed=ok,
            centrality_delta=delta,
            summary=(
                "Pre-fix verification: bugs and proposals generated. "
                "Apply fix in next stage, then re-run Grphify."
            ),
            bugs_found=bugs_count,
            proposals_count=len(proposals),
        )

    def _load_baseline(self) -> dict:
        if not self._metrics_path.exists():
            return {}
        return json.loads(self._metrics_path.read_text(encoding="utf-8"))
