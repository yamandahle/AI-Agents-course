"""chart_generator — pre-generates matplotlib chart PDFs before the LLM draft runs.

Produces three publication-quality PDFs that the draft prompt tells the LLM to
reference via \\includegraphics.  Calling generate_all() is idempotent: existing
PDFs are skipped unless regenerate=True is passed.

Usage (standalone):
    uv run python src/article_writer/tools/chart_generator.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

_STYLE = {"figure.dpi": 150, "axes.spines.top": False, "axes.spines.right": False}


def generate_accuracy_curve(out_dir: Path) -> Path:
    """Training vs validation accuracy over epochs."""
    out = out_dir / "accuracy_curve.pdf"
    rng = np.random.default_rng(42)
    x = np.linspace(0, 30, 120)
    train = np.clip(1 - np.exp(-0.18 * x) + 0.012 * rng.standard_normal(120), 0, 1)
    val = np.clip(1 - np.exp(-0.14 * x) + 0.018 * rng.standard_normal(120), 0, 1)
    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(x, train, linewidth=2, label="Training Accuracy")
        ax.plot(x, val, linewidth=2, linestyle="--", label="Validation Accuracy")
        ax.set_xlabel("Training Epoch")
        ax.set_ylabel("Accuracy")
        ax.set_title("AI Diagnostic Model — Accuracy vs Training Epochs")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(out, format="pdf", bbox_inches="tight")
        plt.close(fig)
    return out


def generate_diagnostic_comparison(out_dir: Path) -> Path:
    """AI vs human expert diagnostic accuracy on five medical imaging tasks."""
    out = out_dir / "diagnostic_comparison.pdf"
    tasks = [
        "Mammography\nScreening",
        "Retinal Scan\nAnalysis",
        "MRI Brain\nTumour",
        "Chest X-Ray\n(Pneumonia)",
        "Skin Lesion\nClassification",
    ]
    ai_acc    = [94.1, 90.3, 91.0, 92.5, 91.0]
    human_acc = [85.2, 87.1, 86.0, 85.8, 78.0]
    x = np.arange(len(tasks))
    width = 0.36
    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(x - width / 2, ai_acc,    width, label="AI Agent",      color="#4C72B0", alpha=0.85)
        ax.bar(x + width / 2, human_acc, width, label="Human Expert",  color="#DD8452", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(tasks, fontsize=9)
        ax.set_ylabel("Diagnostic Accuracy (%)")
        ax.set_title("AI vs Human Expert: Diagnostic Accuracy Across Medical Imaging Tasks")
        ax.set_ylim(70, 100)
        ax.legend()
        ax.grid(axis="y", alpha=0.25)
        for bar in ax.patches:
            ax.annotate(
                f"{bar.get_height():.1f}",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center", va="bottom", fontsize=8,
            )
        fig.tight_layout()
        fig.savefig(out, format="pdf", bbox_inches="tight")
        plt.close(fig)
    return out


def generate_cost_reduction(out_dir: Path) -> Path:
    """Operational cost reduction (%) achieved by AI agents across hospital departments."""
    out = out_dir / "cost_reduction.pdf"
    departments = [
        "Prior Auth\nProcessing",
        "Clinical\nDocumentation",
        "Scheduling &\nAdmissions",
        "Radiology\nWorkflow",
        "Drug\nDispensing",
    ]
    reductions = [67, 40, 35, 28, 52]
    colors = ["#2ca02c" if r >= 50 else "#1f77b4" for r in reductions]
    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ax.barh(departments, reductions, color=colors, alpha=0.82)
        ax.set_xlabel("Cost Reduction (%)")
        ax.set_title("Operational Cost Reduction Achieved by AI Agents in Hospital Departments")
        ax.set_xlim(0, 80)
        ax.bar_label(bars, fmt="%d%%", padding=4, fontsize=9)
        ax.grid(axis="x", alpha=0.25)
        fig.tight_layout()
        fig.savefig(out, format="pdf", bbox_inches="tight")
        plt.close(fig)
    return out


def generate_all(out_dir: Path, *, regenerate: bool = False) -> list[Path]:
    """Generate all three chart PDFs. Skips existing files unless regenerate=True."""
    out_dir.mkdir(parents=True, exist_ok=True)
    generators = [
        generate_accuracy_curve,
        generate_diagnostic_comparison,
        generate_cost_reduction,
    ]
    produced: list[Path] = []
    for fn in generators:
        path = out_dir / (fn.__name__.replace("generate_", "") + ".pdf")
        if path.exists() and not regenerate:
            produced.append(path)
            continue
        produced.append(fn(out_dir))
    return produced


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parent.parent.parent.parent
    paths = generate_all(root / "assets" / "graphs")
    for p in paths:
        print(f"  {p}")
    sys.exit(0)
