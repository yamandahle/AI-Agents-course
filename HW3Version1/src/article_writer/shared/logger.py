"""Structured logger with domain-specific log methods for API calls, tokens, and eval scores."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from article_writer.shared.constants import EVAL_LOG_FILENAME, RESULTS_DIR, RUN_LOG_FILENAME


class ArticleLogger(logging.Logger):
    """Extended logger with domain-specific convenience methods."""

    def log_api_call(self, service: str, query: str, response_preview: str) -> None:
        self.info(
            "[API] service=%s query_len=%d response_len=%d ts=%s",
            service,
            len(query),
            len(response_preview),
            datetime.now(timezone.utc).isoformat(),
        )

    def log_token_usage(
        self,
        service: str,
        input_tok: int,
        output_tok: int,
        cost_usd: float = 0.0,
    ) -> None:
        self.info(
            "[TOKENS] service=%s in=%d out=%d cost=$%.4f",
            service,
            input_tok,
            output_tok,
            cost_usd,
        )

    def log_eval_score(self, iteration: int, scores: dict) -> None:
        self.info("[EVAL] iter=%d scores=%s", iteration, scores)
        log_path = Path(RESULTS_DIR) / EVAL_LOG_FILENAME
        log_path.parent.mkdir(parents=True, exist_ok=True)
        records: list = json.loads(log_path.read_text()) if log_path.exists() else []
        records.append(
            {
                "iteration": iteration,
                "scores": scores,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        log_path.write_text(json.dumps(records, indent=2))


def get_logger(name: str) -> ArticleLogger:
    """Return a named ArticleLogger, creating handlers on first call."""
    logging.setLoggerClass(ArticleLogger)
    log = logging.getLogger(name)
    if not log.handlers:
        log_dir = Path(RESULTS_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s")
        fh = logging.FileHandler(log_dir / RUN_LOG_FILENAME, encoding="utf-8")
        fh.setFormatter(fmt)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        log.addHandler(fh)
        log.addHandler(sh)
        log.setLevel(logging.INFO)
    return log  # type: ignore[return-value]
