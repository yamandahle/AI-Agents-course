"""Phase 3 loop controller — orchestrates the evaluator-optimizer loop."""
from __future__ import annotations

from pathlib import Path

from article_writer.shared.constants import RESULTS_DIR
from article_writer.shared.logger import get_logger
from article_writer.writing.evaluator import Evaluator
from article_writer.writing.optimizer import Optimizer

logger = get_logger(__name__)

_MIN_ITERATIONS = 2


class EvalOptimizerLoop:
    """Runs the evaluator-optimizer loop with minimum 2 iterations enforced."""

    def __init__(
        self,
        max_iterations: int = 3,
        score_threshold: float = 8.0,
        config_model: str = "claude-sonnet-4-6",
    ) -> None:
        self._max_iterations = max_iterations
        self._threshold = score_threshold
        self._model = config_model

    def run(self, initial_draft_path: Path) -> Path:
        """Execute the loop. Returns path to the final draft .tex file."""
        evaluator = Evaluator(config_model=self._model)
        current_draft = initial_draft_path
        last_score = 0.0

        for iteration in range(1, self._max_iterations + 1):
            logger.info("=== Eval-Optimizer loop iteration %d/%d ===", iteration, self._max_iterations)
            score = evaluator.evaluate(current_draft, iteration)
            last_score = score.weighted_score
            logger.info("Iteration %d score: %.2f / 10 (threshold %.1f)", iteration, last_score, self._threshold)

            critique_path = Path(RESULTS_DIR) / f"critique_v{iteration}.md"
            if iteration >= _MIN_ITERATIONS and last_score >= self._threshold:
                logger.info("Score %.2f >= threshold %.1f — stopping loop.", last_score, self._threshold)
                break

            if iteration < self._max_iterations:
                optimizer = Optimizer(iteration=iteration, config_model=self._model)
                current_draft = optimizer.optimize(current_draft, critique_path)

        logger.info("Loop complete. Final score: %.2f. Draft: %s", last_score, current_draft)
        return current_draft
