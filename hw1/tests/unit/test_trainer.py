import json
import pytest
from src.services.train import train_model
from src.services.data_generator import build_datasets
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM

CONFIG_PATH = "config/setup.json"


@pytest.fixture
def config():
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    cfg["training"]["epochs"] = 3
    return cfg


@pytest.fixture
def datasets(config):
    return build_datasets(config, "low", window_size=10)


def test_train_returns_correct_keys(config, datasets):
    train_ds, val_ds = datasets
    result = train_model(FC(window_size=10), train_ds, val_ds, config)
    assert set(result.keys()) == {"train_losses", "val_losses", "best_val_mse", "best_epoch"}


def test_train_loss_history_length(config, datasets):
    train_ds, val_ds = datasets
    result = train_model(FC(window_size=10), train_ds, val_ds, config)
    assert len(result["train_losses"]) == config["training"]["epochs"]
    assert len(result["val_losses"]) == config["training"]["epochs"]


def test_train_loss_decreases(config, datasets):
    train_ds, val_ds = datasets
    result = train_model(FC(window_size=10), train_ds, val_ds, config)
    assert result["train_losses"][-1] < result["train_losses"][0]


def test_best_val_mse_is_minimum(config, datasets):
    train_ds, val_ds = datasets
    result = train_model(FC(window_size=10), train_ds, val_ds, config)
    assert result["best_val_mse"] == pytest.approx(min(result["val_losses"]))


def test_best_epoch_in_range(config, datasets):
    train_ds, val_ds = datasets
    result = train_model(FC(window_size=10), train_ds, val_ds, config)
    assert 0 <= result["best_epoch"] < config["training"]["epochs"]


def test_no_nan_in_losses(config, datasets):
    train_ds, val_ds = datasets
    for model in [FC(10), SignalRNN(10), SignalLSTM(10)]:
        result = train_model(model, train_ds, val_ds, config)
        assert all(loss == loss for loss in result["train_losses"])
        assert all(loss == loss for loss in result["val_losses"])
