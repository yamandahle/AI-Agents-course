"""Plot I/O helpers: save figures as PNG/SVG, export CSV, find Pareto front."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from hw5.shared.config import Config

FRAMEWORK_COLORS: dict[str, str] = {"ollama": "#4472C4", "airllm": "#ED7D31"}
QUANT_LINESTYLES: dict[str, str] = {"Q4": "-", "Q8": "--", "Q2": ":"}
QUANT_MARKERS: dict[str, str] = {"Q4": "o", "Q8": "s", "Q2": "^"}


def results_to_df(results: list[Any]) -> pd.DataFrame:
    """Build flat DataFrame from a list of CellResult objects (duck-typed)."""
    rows = []
    for r in results:
        if r.failed:
            continue
        m, fw, q = r.cell_id.split("__")
        rows.append(
            {
                "model": m,
                "framework": fw,
                "quant": q,
                "failed": r.failed,
                "tokens_per_sec": r.inference.tokens_per_sec,
                "peak_ram_mb": r.metrics.peak_ram_mb,
                "peak_vram_mb": r.metrics.peak_vram_mb,
                "peak_swap_mb": r.metrics.peak_swap_mb,
                "avg_cpu_pct": r.metrics.avg_cpu_pct,
            }
        )
    return pd.DataFrame(rows)


def find_pareto_front(df: pd.DataFrame) -> pd.DataFrame:
    """Return Pareto-optimal rows: max tokens/sec for given peak RAM budget."""
    if df.empty:
        return df
    rows = []
    for _, cand in df.iterrows():
        dominated = df[
            (df["tokens_per_sec"] >= cand["tokens_per_sec"])
            & (df["peak_ram_mb"] <= cand["peak_ram_mb"])
            & (
                (df["tokens_per_sec"] > cand["tokens_per_sec"])
                | (df["peak_ram_mb"] < cand["peak_ram_mb"])
            )
        ]
        if dominated.empty:
            rows.append(cand.to_dict())
    return pd.DataFrame(rows)


def plot_tradeoff_scatter(
    df: pd.DataFrame,
    fig_size: tuple,
    pareto_fn: Any,
) -> plt.Figure:
    """Scatter: peak RAM (x) vs tokens/sec (y) with Pareto frontier."""
    fig, ax = plt.subplots(figsize=fig_size)
    for _, row in df.iterrows():
        ax.scatter(
            row["peak_ram_mb"],
            row["tokens_per_sec"],
            c=FRAMEWORK_COLORS.get(row["framework"], "grey"),
            marker=QUANT_MARKERS.get(row["quant"], "o"),
            s=120,
            zorder=3,
        )
        ax.annotate(
            f"{row['model']}/{row['quant']}",
            (row["peak_ram_mb"], row["tokens_per_sec"]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
        )
    pareto = pareto_fn(df)
    if not pareto.empty:
        p = pareto.sort_values("peak_ram_mb")
        ax.step(
            p["peak_ram_mb"],
            p["tokens_per_sec"],
            where="post",
            color="grey",
            lw=1.5,
            ls="--",
        )
    ax.set_xlabel("Peak RAM (MB)")
    ax.set_ylabel("Tokens/sec")
    fig.tight_layout()
    return fig


def save_all(plotter: Any, config: Config) -> list[Path]:
    """Save all four charts as .png and .svg; return list of 8 paths."""
    out = Path(config.assets_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    charts = [
        ("heatmap", plotter.heatmap()),
        ("ram_timeline", plotter.ram_timeline()),
        ("vram_bar", plotter.vram_bar_chart()),
        ("tradeoff_scatter", plotter.tradeoff_scatter()),
    ]
    for name, fig in charts:
        for ext in ("png", "svg"):
            p = out / f"{name}.{ext}"
            fig.savefig(str(p), dpi=plotter._dpi, bbox_inches="tight")
            paths.append(p)
        plt.close(fig)
    return paths


def save_csv(df: pd.DataFrame, path: str | Path | None, config: Config) -> Path:
    """Export a results DataFrame to CSV and return the file path."""
    out = Path(path) if path else Path(config.assets_dir) / "results.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(out), index=False)
    return out
