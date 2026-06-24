"""Plotter — matplotlib/seaborn visualizations for evaluation results."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from hw5.services import plot_io as _pio
from hw5.services.cell_result import CellResult
from hw5.services.plot_io import FRAMEWORK_COLORS, QUANT_LINESTYLES
from hw5.shared.config import Config


class Plotter:
    """Four standard charts from CellResult evaluation data."""

    _fig_size: tuple = (12, 8)
    _dpi: int = 300

    def __init__(self, results: list[CellResult], config: Config) -> None:
        self._results = results
        self._config = config

    def _get_df(self) -> pd.DataFrame:
        return _pio.results_to_df(self._results)

    def heatmap(self) -> plt.Figure:
        """Seaborn heatmap of tokens/sec — one subplot per model."""
        df = self._get_df()
        models = list(df["model"].unique()) if not df.empty else []
        fig, axes = plt.subplots(1, max(len(models), 1), figsize=self._fig_size)
        axes = [axes] if len(models) <= 1 else list(axes)
        for ax, model in zip(axes, models):
            pivot = df[df["model"] == model].pivot_table(
                index="framework", columns="quant", values="tokens_per_sec"
            )
            sns.heatmap(
                pivot,
                ax=ax,
                cmap="RdYlGn",
                annot=True,
                fmt=".1f",
                cbar_kws={"label": "Tokens/sec"},
            )
            ax.set_title(model)
        fig.tight_layout()
        return fig

    def ram_timeline(self) -> plt.Figure:
        """Line chart: RAM MB vs time (s) for each successful cell."""
        fig, ax = plt.subplots(figsize=self._fig_size)
        for r in self._results:
            if r.failed or not r.metrics.samples:
                continue
            fw, quant = r.cell_id.split("__")[1], r.cell_id.split("__")[2]
            ax.plot(
                [s["ts"] for s in r.metrics.samples],
                [s["ram"] for s in r.metrics.samples],
                color=FRAMEWORK_COLORS.get(fw, "grey"),
                linestyle=QUANT_LINESTYLES.get(quant, "-"),
                label=r.cell_id,
            )
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("RAM Used (MB)")
        ax.legend(fontsize=6, loc="upper left")
        fig.tight_layout()
        return fig

    def vram_bar_chart(self) -> plt.Figure:
        """Bar chart of peak VRAM per cell, colored by framework."""
        df = self._get_df()
        fig, ax = plt.subplots(figsize=self._fig_size)
        if df.empty:
            return fig
        bars = ax.bar(
            range(len(df)),
            df["peak_vram_mb"],
            color=[FRAMEWORK_COLORS.get(fw, "grey") for fw in df["framework"]],
        )
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(
            [f"{r.model}\n{r.quant}" for _, r in df.iterrows()], rotation=45, ha="right"
        )
        ax.set_ylabel("Peak VRAM (MB)")
        for bar, val in zip(bars, df["peak_vram_mb"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.0f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        fig.tight_layout()
        return fig

    def tradeoff_scatter(self) -> plt.Figure:
        """Scatter: peak RAM (x) vs tokens/sec (y) with Pareto frontier."""
        return _pio.plot_tradeoff_scatter(
            self._get_df(), self._fig_size, self._find_pareto_front
        )

    @staticmethod
    def _find_pareto_front(df: pd.DataFrame) -> pd.DataFrame:
        """Return Pareto-optimal rows: max tokens/sec for given RAM budget."""
        return _pio.find_pareto_front(df)

    def save_all(self) -> list[Path]:
        """Save all four charts as .png and .svg; return list of 8 paths."""
        return _pio.save_all(self, self._config)

    def save_csv(self, path: str | Path | None = None) -> Path:
        """Export results DataFrame to CSV and return the path."""
        return _pio.save_csv(self._get_df(), path, self._config)
