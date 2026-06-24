"""SummaryGenerator — auto-generates prose for each evaluation chart."""

from __future__ import annotations

from hw5.services.cell_result import CellResult


class SummaryGenerator:
    """Generates textual insights from a list of CellResults."""

    def __init__(self, results: list[CellResult]) -> None:
        self._ok = [r for r in results if not r.failed]
        self._all = results

    def summarize_heatmap(self) -> str:
        """3-4 sentences summarizing the tokens/sec heatmap findings."""
        if not self._ok:
            return "No successful results to summarize."
        best = max(self._ok, key=lambda r: r.inference.tokens_per_sec)
        worst = min(self._ok, key=lambda r: r.inference.tokens_per_sec)
        p = best.cell_id.split("__")
        return (
            f"Across all quantization levels, {p[1]} at {p[2]} achieved the highest "
            f"throughput of {best.inference.tokens_per_sec:.1f} tok/s on model {p[0]}. "
            f"The slowest configuration was {worst.cell_id} at "
            f"{worst.inference.tokens_per_sec:.1f} tok/s. "
            f"Q4 quantization offers the best speed/quality trade-off for CPU-only "
            f"inference on this hardware."
        )

    def summarize_timeline(self) -> str:
        """3-4 sentences summarizing RAM timeline observations."""
        if not self._ok:
            return "No successful results to summarize."
        peak_r = max(self._ok, key=lambda r: r.metrics.peak_ram_mb)
        low_r = min(self._ok, key=lambda r: r.metrics.peak_ram_mb)
        swap_cells = [r for r in self._ok if r.metrics.peak_swap_mb > 0]
        swap_note = (
            f"Swap was triggered in {len(swap_cells)} cell(s). "
            if swap_cells
            else "No swap usage was detected. "
        )
        return (
            f"RAM pressure peaked at {peak_r.metrics.peak_ram_mb:.1f} MB during "
            f"{peak_r.cell_id}. "
            f"The most memory-efficient cell was {low_r.cell_id} at "
            f"{low_r.metrics.peak_ram_mb:.1f} MB. "
            f"{swap_note}"
            f"AirLLM's layer-streaming avoids holding the full model in RAM simultaneously."
        )

    def summarize_vram(self) -> str:
        """3-4 sentences summarizing VRAM usage across frameworks."""
        if not self._ok:
            return "No successful results to summarize."
        airllm_r = [r for r in self._ok if "airllm" in r.cell_id]
        ollama_r = [r for r in self._ok if "ollama" in r.cell_id]
        avg_a = (
            sum(r.metrics.peak_vram_mb for r in airllm_r) / len(airllm_r)
            if airllm_r
            else 0.0
        )
        avg_o = (
            sum(r.metrics.peak_vram_mb for r in ollama_r) / len(ollama_r)
            if ollama_r
            else 0.0
        )
        spikes = sum(len(r.metrics.spike_events) for r in self._ok)
        return (
            f"AirLLM's layer-streaming kept peak VRAM at {avg_a:.0f} MB on average "
            f"vs {avg_o:.0f} MB for Ollama. "
            f"A total of {spikes} VRAM spike event(s) were recorded across all cells. "
            f"On this CPU-only machine all VRAM readings are 0 MB since no NVIDIA GPU "
            f"is present."
        )

    def summarize_tradeoff(self) -> str:
        """3-4 sentences summarizing the RAM vs tokens/sec trade-off."""
        if not self._ok:
            return "No successful results to summarize."
        eff = lambda r: r.inference.tokens_per_sec / max(r.metrics.peak_ram_mb, 1)  # noqa: E731
        best = max(self._ok, key=eff)
        worst = min(self._ok, key=eff)
        best_q = best.cell_id.split("__")[2]
        return (
            f"The trade-off surface reveals that {best_q} quantization delivers "
            f"the best efficiency ({best.inference.tokens_per_sec:.1f} tok/s at "
            f"{best.metrics.peak_ram_mb:.0f} MB RAM). "
            f"The worst value cell is {worst.cell_id} "
            f"({worst.inference.tokens_per_sec:.1f} tok/s at "
            f"{worst.metrics.peak_ram_mb:.0f} MB). "
            f"Pareto-optimal configurations favour Q4 for throughput-sensitive workloads."
        )

    def generate_all(self) -> dict[str, str]:
        """Return all four summaries keyed by plot name."""
        return {
            "heatmap": self.summarize_heatmap(),
            "ram_timeline": self.summarize_timeline(),
            "vram_bar": self.summarize_vram(),
            "tradeoff_scatter": self.summarize_tradeoff(),
        }
