import torch
import pytest
from src.sdk.models.fc import FC
from src.sdk.models.rnn import SignalRNN
from src.sdk.models.lstm import SignalLSTM
from src.sdk.models.base import BaseModel

BATCH = 8
W_SIZES = [5, 10, 20]


@pytest.mark.parametrize("W", W_SIZES)
def test_fc_output_shape(W):
    model = FC(window_size=W)
    x = torch.randn(BATCH, W + 5)
    out = model(x)
    assert out.shape == (BATCH, W)


@pytest.mark.parametrize("W", W_SIZES)
def test_rnn_output_shape(W):
    model = SignalRNN(window_size=W)
    x = torch.randn(BATCH, W + 5)
    out = model(x)
    assert out.shape == (BATCH, W)


@pytest.mark.parametrize("W", W_SIZES)
def test_lstm_output_shape(W):
    model = SignalLSTM(window_size=W)
    x = torch.randn(BATCH, W + 5)
    out = model(x)
    assert out.shape == (BATCH, W)


def test_fc_is_base_model():
    assert issubclass(FC, BaseModel)


def test_rnn_is_base_model():
    assert issubclass(SignalRNN, BaseModel)


def test_lstm_is_base_model():
    assert issubclass(SignalLSTM, BaseModel)


def test_fc_save_load(tmp_path):
    model = FC(window_size=10)
    path = str(tmp_path / "mlp.pt")
    model.save(path)
    model2 = FC(window_size=10)
    model2.load(path)
    x = torch.randn(4, 15)
    torch.testing.assert_close(model(x), model2(x))


def test_rnn_save_load(tmp_path):
    model = SignalRNN(window_size=10)
    path = str(tmp_path / "rnn.pt")
    model.save(path)
    model2 = SignalRNN(window_size=10)
    model2.load(path)
    x = torch.randn(4, 15)
    torch.testing.assert_close(model(x), model2(x))


def test_lstm_save_load(tmp_path):
    model = SignalLSTM(window_size=10)
    path = str(tmp_path / "lstm.pt")
    model.save(path)
    model2 = SignalLSTM(window_size=10)
    model2.load(path)
    x = torch.randn(4, 15)
    torch.testing.assert_close(model(x), model2(x))


@pytest.mark.parametrize("W", W_SIZES)
def test_models_no_nan(W):
    x = torch.randn(BATCH, W + 5)
    for model in [FC(W), SignalRNN(W), SignalLSTM(W)]:
        out = model(x)
        assert not torch.isnan(out).any()
