"""Generate a matplotlib graph and save as PDF for LaTeX inclusion."""
from __future__ import annotations

import argparse
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate(title: str, xlabel: str, ylabel: str, output: str) -> None:
    x = np.linspace(0, 10, 100)
    y_train = 1 - np.exp(-0.5 * x) + 0.02 * np.random.default_rng(42).standard_normal(100)
    y_val = 1 - np.exp(-0.4 * x) + 0.03 * np.random.default_rng(7).standard_normal(100)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, np.clip(y_train, 0, 1), label="Training", linewidth=2)
    ax.plot(x, np.clip(y_val, 0, 1), label="Validation", linewidth=2, linestyle="--")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, format="pdf", bbox_inches="tight")
    print(f"Graph saved: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a graph PDF for LaTeX inclusion")
    parser.add_argument("--title", default="Model Accuracy Over Epochs")
    parser.add_argument("--xlabel", default="Epoch")
    parser.add_argument("--ylabel", default="Accuracy")
    parser.add_argument("--output", default="assets/graphs/accuracy_curve.pdf")
    args = parser.parse_args()
    generate(args.title, args.xlabel, args.ylabel, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
