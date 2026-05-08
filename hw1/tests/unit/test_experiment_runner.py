"""Tests for experiment_runner.py — ExperimentResult, save_results, run logic."""
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
import torch
from torch.utils.data import TensorDataset, DataLoader

from src.services.experiment_runner import (
    ExperimentResult,
    save_results,
    run_experiments,
    _per_signal_mse,
)
from src.sdk.models.fc import FC


# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_result():
    return ExperimentResult(
        signal="S1",
        noise_level="low",
        window_size=10,
        model="FC",
        best_mse=0.05,
        best_epoch=3,
        train_losses=[0.5, 0.3, 0.2, 0.15],
        val_losses=[0.6, 0.35, 0.22, 0.18],
    )


@pytest.fixture
def tiny_config():
    return {
        "signal": {"frequencies": [1, 2, 5, 10], "amplitude": 1.0,
                   "phase": 0, "duration": 10, "sample_rate": 1000},
        "noise": {"low": {"alpha": 0.05, "beta": 0.05}},
        "data": {"window_sizes": [10], "default_window": 10,
                 "train_ratio": 0.8, "seed": 42},
        "models": {"hidden_size": 128, "num_layers": 2, "fc_hidden": 256},
        "training": {"epochs": 3, "batch_size": 64, "lr": 0.001},
    }


# ── ExperimentResult tests ────────────────────────────────────────────────────

def test_experiment_result_fields(sample_result):
    assert sample_result.signal == "S1"
    assert sample_result.noise_level == "low"
    assert sample_result.window_size == 10
    assert sample_result.model == "FC"
    assert sample_result.best_mse == pytest.approx(0.05)
    assert sample_result.best_epoch == 3
    assert len(sample_result.train_losses) == 4
    assert len(sample_result.val_losses) == 4


def test_experiment_result_as_dict(sample_result):
    from dataclasses import asdict
    d = asdict(sample_result)
    assert d["signal"] == "S1"
    assert d["best_mse"] == pytest.approx(0.05)
    assert isinstance(d["train_losses"], list)


# ── save_results tests ────────────────────────────────────────────────────────

def test_save_results_creates_file(sample_result):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "sub", "results.json")
        save_results([sample_result], path)
        assert os.path.exists(path)


def test_save_results_json_content(sample_result):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "results.json")
        save_results([sample_result, sample_result], path)
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["signal"] == "S1"
        assert data[0]["best_mse"] == pytest.approx(0.05)


def test_save_results_roundtrip(sample_result):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "results.json")
        save_results([sample_result], path)
        with open(path) as f:
            loaded = [ExperimentResult(**r) for r in json.load(f)]
        assert loaded[0].signal == sample_result.signal
        assert loaded[0].best_mse == pytest.approx(sample_result.best_mse)


# ── _per_signal_mse tests ─────────────────────────────────────────────────────

def test_per_signal_mse_returns_float():
    W = 10
    model = FC(W)
    # Need 4 × N_EVAL × W = 4 × 200 × 10 = 8000 entries to avoid OOB
    n_windows = 8000
    xs = torch.randn(n_windows, W + 4)
    ys = torch.randn(n_windows, W)
    full_ds = TensorDataset(xs, ys)
    mse = _per_signal_mse(model, full_ds, sig_idx=0, W=W)
    assert isinstance(mse, float)
    assert mse >= 0.0


def test_per_signal_mse_no_nan():
    W = 10
    model = FC(W)
    n_windows = 8000
    xs = torch.randn(n_windows, W + 4)
    ys = torch.randn(n_windows, W)
    full_ds = TensorDataset(xs, ys)
    for sig_idx in range(4):
        mse = _per_signal_mse(model, full_ds, sig_idx=sig_idx, W=W)
        assert mse == mse  # NaN check


# ── run_experiments tests (mocked) ────────────────────────────────────────────

def _make_fake_ds(W=10, n=800):
    xs = torch.randn(n, W + 4)
    ys = torch.randn(n, W)
    full_ds = TensorDataset(xs, ys)
    subset = torch.utils.data.Subset(full_ds, range(640))
    return DataLoader(subset, batch_size=64), DataLoader(
        torch.utils.data.Subset(full_ds, range(640, 800)), batch_size=64
    )


def _large_fake_val():
    """Return a mock val DataLoader whose .dataset has 8000 entries."""
    fake_val = MagicMock()
    fake_val.dataset = TensorDataset(
        torch.randn(8000, 14), torch.randn(8000, 10)
    )
    return fake_val


def test_run_experiments_returns_list(tiny_config):
    fake_train_result = {
        "train_losses": [0.5, 0.4, 0.3],
        "val_losses": [0.6, 0.5, 0.4],
        "best_val_mse": 0.4,
        "best_epoch": 2,
    }

    with patch("src.services.experiment_runner.build_datasets",
               return_value=(MagicMock(), _large_fake_val())), \
         patch("src.services.experiment_runner.train_model",
               return_value=fake_train_result):
        results = run_experiments(tiny_config)

    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, ExperimentResult) for r in results)


def test_run_experiments_fast_flag(tiny_config):
    fake_train_result = {
        "train_losses": [0.5] * 10,
        "val_losses": [0.6] * 10,
        "best_val_mse": 0.5,
        "best_epoch": 5,
    }

    with patch("src.services.experiment_runner.build_datasets",
               return_value=(MagicMock(), _large_fake_val())), \
         patch("src.services.experiment_runner.train_model",
               return_value=fake_train_result) as mock_train:
        run_experiments(tiny_config, fast=True)
        # fast=True should cap epochs at 10
        called_config = mock_train.call_args[0][3]
        assert called_config["training"]["epochs"] == 10


def test_run_experiments_result_fields(tiny_config):
    fake_train_result = {
        "train_losses": [0.5, 0.4, 0.3],
        "val_losses": [0.6, 0.5, 0.4],
        "best_val_mse": 0.4,
        "best_epoch": 2,
    }

    with patch("src.services.experiment_runner.build_datasets",
               return_value=(MagicMock(), _large_fake_val())), \
         patch("src.services.experiment_runner.train_model",
               return_value=fake_train_result):
        results = run_experiments(tiny_config)

    r = results[0]
    assert r.noise_level in tiny_config["noise"]
    assert r.window_size in tiny_config["data"]["window_sizes"]
    assert r.model in ("FC", "RNN", "LSTM")
    assert r.signal in ("S1", "S2", "S3", "S4")
    assert isinstance(r.best_mse, float)
