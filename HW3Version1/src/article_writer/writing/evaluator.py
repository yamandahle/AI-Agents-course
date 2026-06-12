"""Phase 3a — evaluates draft on 5 weighted dimensions and writes structured critique."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from article_writer.shared.constants import DEFAULT_ENCODING, RESULTS_DIR
from article_writer.shared.gatekeeper import ApiGatekeeper
from article_writer.shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_EVAL_PROMPT = (
    "Evaluate this LaTeX article draft on 5 dimensions (score each 1-10):\n"
    "1. Coverage (25%): Are all guideline key points addressed?\n"
    "2. Accuracy (25%): Are all claims backed by citations?\n"
    "3. Style (20%): Does writing match the Characters.md profile?\n"
    "4. Structure (20%): Does it follow Structure.md?\n"
    "5. Citation Quality (10%): IEEE format, valid URLs?\n\n"
    "Draft:\n{draft}\n\n"
    "Return JSON only: {{\"coverage\": N, \"accuracy\": N, \"style\": N, "
    "\"structure\": N, \"citation_quality\": N, \"critique_points\": [...]}}"
)
_WEIGHTS = {"coverage": 0.25, "accuracy": 0.25, "style": 0.20, "structure": 0.20, "citation_quality": 0.10}


@dataclass
class EvaluationScore:
    coverage: float
    accuracy: float
    style: float
    structure: float
    citation_quality: float
    weighted_score: float
    critique_points: list[str]


class Evaluator:
    """Scores the draft and produces structured critique for the optimizer."""

    def __init__(self, config_model: str = "claude-sonnet-4-6") -> None:
        self._model = config_model
        self._gate = ApiGatekeeper()

    def evaluate(self, draft_path: Path, iteration: int) -> EvaluationScore:
        draft = draft_path.read_text(encoding=DEFAULT_ENCODING)
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        def _call() -> anthropic.types.Message:
            return client.messages.create(
                model=self._model,
                max_tokens=1024,
                messages=[{"role": "user", "content": _EVAL_PROMPT.format(draft=draft[:6000])}],
            )

        response = self._gate.execute("anthropic", _call)
        data = json.loads(response.content[0].text)
        scores = {k: max(1.0, min(10.0, float(data.get(k, 5)))) for k in _WEIGHTS}
        weighted = sum(scores[k] * w for k, w in _WEIGHTS.items())
        critique_points = data.get("critique_points", [])
        score = EvaluationScore(**scores, weighted_score=round(weighted, 2), critique_points=critique_points)
        self._write_critique(score, iteration)
        logger.log_eval_score(iteration, {**scores, "weighted": weighted})
        return score

    def _write_critique(self, score: EvaluationScore, iteration: int) -> None:
        path = Path(RESULTS_DIR) / f"critique_v{iteration}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Critique — Iteration {iteration}", f"Weighted Score: {score.weighted_score}/10", ""]
        lines += [f"- {pt}" for pt in score.critique_points]
        path.write_text("\n".join(lines), encoding=DEFAULT_ENCODING)
