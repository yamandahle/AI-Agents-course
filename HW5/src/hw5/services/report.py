"""ReportGenerator — self-contained HTML report with embedded charts."""

from __future__ import annotations

import base64
import time
from pathlib import Path

from hw5.services.cell_result import CellResult

_CSS = (
    "body{font-family:Arial,sans-serif;max-width:1200px;margin:0 auto;padding:20px}"
    "table{border-collapse:collapse;width:100%;margin:1em 0}"
    "th,td{border:1px solid #ddd;padding:8px;text-align:left}"
    "tr:nth-child(even){background:#f2f2f2}"
    "th{background:#4472C4;color:white}"
    "img{max-width:100%;height:auto}"
    "@media print{.no-print{display:none}}"
)

_COLS = (
    "cell_id",
    "tokens_per_sec",
    "peak_ram_mb",
    "peak_vram_mb",
    "avg_cpu_pct",
    "failed",
)


class ReportGenerator:
    """Assembles an HTML report with embedded charts, summaries, and metrics table."""

    def __init__(
        self,
        summaries: dict[str, str],
        plot_paths: dict[str, Path],
        results: list[CellResult],
    ) -> None:
        self._summaries = summaries
        self._plot_paths = plot_paths
        self._results = results

    def _embed(self, path: Path) -> str:
        """Return an <img> tag with a base64 data URI, or a fallback message."""
        if not path.exists():
            return f"<p>Image not found: {path.name}</p>"
        data = base64.b64encode(path.read_bytes()).decode()
        ext = path.suffix.lstrip(".")
        mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
        return f'<img src="data:{mime};base64,{data}" alt="{path.stem}">'

    def _metrics_table(self) -> str:
        """Render a full metrics table as HTML."""
        header = "".join(f"<th>{c}</th>" for c in _COLS)
        rows = ""
        for r in self._results:
            vals = [
                r.cell_id,
                f"{r.inference.tokens_per_sec:.2f}",
                f"{r.metrics.peak_ram_mb:.1f}",
                f"{r.metrics.peak_vram_mb:.1f}",
                f"{r.metrics.avg_cpu_pct:.1f}",
                str(r.failed),
            ]
            rows += "<tr>" + "".join(f"<td>{v}</td>" for v in vals) + "</tr>"
        return f"<table><tr>{header}</tr>{rows}</table>"

    def to_html(self) -> str:
        """Render the full HTML report as a string."""
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        sections = ""
        for name, summary in self._summaries.items():
            png = self._plot_paths.get(f"{name}.png", Path(f"{name}.png"))
            sections += (
                f'<section id="{name}">'
                f"<h2>{name.replace('_', ' ').title()}</h2>"
                f"{self._embed(png)}<p>{summary}</p></section>"
            )
        return (
            "<!DOCTYPE html><html>"
            "<head><meta charset='utf-8'>"
            "<title>HW5 Evaluation Report</title>"
            f"<style>{_CSS}</style></head><body>"
            "<h1>AirLLM vs Ollama Evaluation Report</h1>"
            f"<p>Generated: {ts}</p>"
            f"{sections}"
            "<section id='metrics'><h2>Full Metrics Table</h2>"
            f"{self._metrics_table()}</section>"
            "</body></html>"
        )

    def save(self, path: str | Path | None = None) -> Path:
        """Write the HTML report to disk and return its path."""
        out = Path(path) if path else Path("assets/report.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
        return out
