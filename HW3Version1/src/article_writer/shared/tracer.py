"""Append-only JSONL tracer — logs every LLM/tool call with full I/O and metadata."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_DEFAULT_PATH = Path("results/traces.jsonl")


class Tracer:
    """Thread-safe JSONL appender for LLM and tool call traces."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path or os.getenv("TRACES_FILE", str(_DEFAULT_PATH)))
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        step: str,
        model: str,
        provider: str = "unknown",
        input: str = "",
        output: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        tool_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        record = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "step": step,
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input": input[:6000],
            "output": output[:6000],
        }
        if tool_name:
            record["tool_name"] = tool_name
        if metadata:
            record["metadata"] = metadata
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_tool(
        self,
        *,
        tool_name: str,
        input_data: Any,
        output_data: Any,
        step: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.log(
            step=step or f"tool:{tool_name}",
            model="tool",
            provider="tool",
            tool_name=tool_name,
            input=json.dumps(input_data, ensure_ascii=False, default=str)[:6000],
            output=json.dumps(output_data, ensure_ascii=False, default=str)[:6000],
            metadata=metadata,
        )

    def read_all(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self._path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
