import json
import numpy as np
import pytest
import torch
from src.services.data_generator import SignalGenerator, SineDataset, build_datasets, NUM_SIGNALS

CONFIG_PATH = "config/setup.json"


@pytest.fixture
def config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


@pytest.fixture
def gen(config):
    return SignalGenerator(config)


# --- SignalGenerator ---

def test_clean_signal_length(gen, config):
    expected = config["signal"]["sample_rate"] * config["signal"]["duration"]
    for i in range(NUM_SIGNALS):
        assert len(gen.clean(i)) == expected


def test_clean_s1_to_s4_are_sine(gen):
    for i in range(4):
        sig = gen.clean(i)
        assert np.max(np.abs(sig)) <= 1.0 + 1e-6


def test_s5_is_sum_of_s1_to_s4(gen):
    s5 = gen.clean(4)
    expected = sum(gen.clean(i) for i in range(4))
    np.testing.assert_allclose(s5, expected, rtol=1e-5)


def test_noisy_window_shape(gen, config):
    W = config["data"]["default_window"]
    noisy = gen.noisy_window(0, 0, W, alpha=0.1, beta=0.1)
    assert noisy.shape == (W,)


def test_noisy_window_differs_from_clean(gen, config):
    W = config["data"]["default_window"]
    clean_win = gen.clean(0)[:W]
    noisy_win = gen.noisy_window(0, 0, W, alpha=0.3, beta=0.3)
    assert not np.allclose(clean_win, noisy_win)


def test_noisy_window_s5_shape(gen, config):
    W = config["data"]["default_window"]
    noisy = gen.noisy_window(4, 0, W, alpha=0.1, beta=0.1)
    assert noisy.shape == (W,)


# --- SineDataset ---

def test_dataset_input_shape(config):
    W = config["data"]["default_window"]
    ds = SineDataset(config, "low", W)
    x, y = ds[0]
    assert x.shape == (W + NUM_SIGNALS,)
    assert y.shape == (W,)


def test_dataset_one_hot_prefix(config):
    W = config["data"]["default_window"]
    ds = SineDataset(config, "low", W)
    for idx in range(min(len(ds), 100)):
        x, _ = ds[idx]
        one_hot = x[:NUM_SIGNALS].numpy()
        assert one_hot.sum() == pytest.approx(1.0)
        assert set(one_hot).issubset({0.0, 1.0})


def test_dataset_normalized(config):
    W = config["data"]["default_window"]
    ds = SineDataset(config, "low", W)
    targets = torch.stack([ds[i][1] for i in range(min(len(ds), 500))])
    assert targets.abs().max().item() <= 1.0 + 1e-5


def test_dataset_size(config):
    W = config["data"]["default_window"]
    ds = SineDataset(config, "low", W)
    n_samples_per_signal = config["signal"]["sample_rate"] * config["signal"]["duration"] - W
    assert len(ds) == NUM_SIGNALS * n_samples_per_signal


def test_dataset_three_noise_levels(config):
    W = config["data"]["default_window"]
    for level in ("low", "med", "high"):
        ds = SineDataset(config, level, W)
        assert len(ds) > 0


# --- build_datasets ---

def test_build_datasets_split(config):
    W = config["data"]["default_window"]
    train_ds, test_ds = build_datasets(config, "low", W)
    total = len(train_ds) + len(test_ds)
    ratio = len(train_ds) / total
    assert abs(ratio - config["data"]["train_ratio"]) < 0.01


def test_build_datasets_window_sizes(config):
    for W in config["data"]["window_sizes"]:
        train_ds, test_ds = build_datasets(config, "low", W)
        x, y = train_ds[0]
        assert x.shape == (W + NUM_SIGNALS,)
        assert y.shape == (W,)
