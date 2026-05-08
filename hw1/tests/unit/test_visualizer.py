"""Tests for ResearchVisualizer — plot methods and report saving."""
import os
import tempfile
import numpy as np
import pytest
import matplotlib
matplotlib.use("Agg")

from src.services.research_visualizer import ResearchVisualizer


@pytest.fixture
def viz(tmp_path):
    return ResearchVisualizer(output_dir=str(tmp_path))


@pytest.fixture
def dummy_history():
    t = np.linspace(0, 5, 50)
    return {
        "FC":   np.exp(-t) * 0.1,
        "RNN":  np.exp(-t) * 0.05,
        "LSTM": np.exp(-t) * 0.02,
    }


@pytest.fixture
def dummy_signal():
    t = np.linspace(0, 2 * np.pi, 100)
    pure = np.sin(t)
    noisy = pure + np.random.default_rng(0).normal(0, 0.1, 100)
    predicted = pure + np.random.default_rng(1).normal(0, 0.02, 100)
    return pure, noisy, predicted


# ── constructor ──────────────────────────────────────────────────────────────

def test_init_creates_output_dir(tmp_path):
    new_dir = os.path.join(str(tmp_path), "nested", "outputs")
    viz = ResearchVisualizer(output_dir=new_dir)
    assert os.path.isdir(new_dir)
    assert viz.output_dir == new_dir


# ── plot_mse_curves ──────────────────────────────────────────────────────────

def test_plot_mse_curves_saves_png(viz, dummy_history):
    viz.plot_mse_curves(dummy_history)
    assert os.path.exists(os.path.join(viz.output_dir, "mse_curves.png"))


def test_plot_mse_curves_single_model(viz):
    history = {"FC": np.linspace(0.5, 0.1, 30)}
    viz.plot_mse_curves(history)
    assert os.path.exists(os.path.join(viz.output_dir, "mse_curves.png"))


# ── plot_signal_comparison ───────────────────────────────────────────────────

def test_plot_signal_comparison_saves_png(viz, dummy_signal):
    pure, noisy, predicted = dummy_signal
    viz.plot_signal_comparison(pure, noisy, predicted, title="TestRun")
    assert os.path.exists(
        os.path.join(viz.output_dir, "signal_testrun.png")
    )


def test_plot_signal_comparison_default_title(viz, dummy_signal):
    pure, noisy, predicted = dummy_signal
    viz.plot_signal_comparison(pure, noisy, predicted)
    assert os.path.exists(
        os.path.join(viz.output_dir, "signal_reconstruction.png")
    )


# ── save_final_report ────────────────────────────────────────────────────────

def test_save_final_report_creates_file(viz):
    metrics = {"FC": 0.082, "RNN": 0.153, "LSTM": 0.092}
    viz.save_final_report(metrics)
    assert os.path.exists(os.path.join(viz.output_dir, "summary.txt"))


def test_save_final_report_content(viz):
    metrics = {"FC": 0.082, "RNN": 0.153}
    viz.save_final_report(metrics)
    with open(os.path.join(viz.output_dir, "summary.txt")) as f:
        content = f.read()
    assert "FC" in content
    assert "RNN" in content
    assert "MSE=" in content
    assert "HW1 Final Comparison Report" in content


# ── hw1 package smoke test ────────────────────────────────────────────────────

def test_hw1_hello():
    from src.hw1 import hello
    assert hello() == "Hello from hw1!"
