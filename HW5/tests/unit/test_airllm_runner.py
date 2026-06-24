"""T383–T400: Unit tests for AirLLMRunner (all heavy imports mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import torch

from hw5.services.airllm_runner import AirLLMRunner, RunnerError, UnsupportedQuantError
from hw5.services.runner_protocol import InferenceResult
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

# ── helpers ───────────────────────────────────────────────────────────────────

_PROMPT_LEN = 5
_OUT_LEN = 8  # 5 prompt + 3 generated


def _fast_gk() -> ApiGatekeeper:
    return ApiGatekeeper(rate=1000.0, burst=100)


def _runner(config) -> AirLLMRunner:
    return AirLLMRunner(config, _fast_gk())


def _mock_tokenizer() -> MagicMock:
    tok = MagicMock()
    tok.return_value.input_ids = torch.zeros(1, _PROMPT_LEN, dtype=torch.long)
    tok.eos_token = "</s>"
    tok.pad_token = None
    tok.decode.return_value = "generated text"
    return tok


def _mock_model(out_len: int = _OUT_LEN) -> MagicMock:
    m = MagicMock()
    m.generate.return_value = torch.zeros(1, out_len, dtype=torch.long)
    return m


# ── T389: health_check ────────────────────────────────────────────────────────


@patch("hw5.services.airllm_runner._AIRLLM_AVAILABLE", True)
def test_health_check_true_when_airllm_importable(config):
    assert _runner(config).health_check() is True


@patch("hw5.services.airllm_runner._AIRLLM_AVAILABLE", False)
def test_health_check_false_when_airllm_not_importable(config):
    assert _runner(config).health_check() is False


# ── T391: _resolve_compression ────────────────────────────────────────────────


def test_resolve_compression_q4_returns_4bit(config):
    assert (
        _runner(config)._resolve_compression(QuantizationConfig.from_label("Q4"))
        == "4bit"
    )


def test_resolve_compression_q8_returns_8bit(config):
    assert (
        _runner(config)._resolve_compression(QuantizationConfig.from_label("Q8"))
        == "8bit"
    )


# ── T392: UnsupportedQuantError for Q2 ───────────────────────────────────────


def test_resolve_compression_q2_raises_unsupported(config):
    with pytest.raises(UnsupportedQuantError, match="Q2"):
        _runner(config)._resolve_compression(QuantizationConfig.from_label("Q2"))


# ── T383/T384: load calls from_pretrained ────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_load_calls_from_pretrained_with_compression(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("Qwen/Qwen2.5-1.5B-Instruct", QuantizationConfig.from_label("Q4"))
    call_kwargs = mock_airllm.from_pretrained.call_args
    assert call_kwargs.kwargs.get("compression") == "4bit"


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_load_stores_model_id_and_quant(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    quant = QuantizationConfig.from_label("Q4")
    runner.load("some/model", quant)
    assert runner._model_id == "some/model"
    assert runner._quant is quant


# ── T385: load raises on failure ──────────────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_load_raises_runner_error_on_failure(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.side_effect = RuntimeError("OOM")
    with pytest.raises(RunnerError, match="OOM"):
        _runner(config).load("some/model", QuantizationConfig.from_label("Q4"))


# ── T394: unload is no-op when nothing loaded ─────────────────────────────────


def test_unload_with_no_model_is_noop(config):
    _runner(config).unload()  # must not raise


# ── T388: unload clears model reference ──────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_unload_clears_model_and_tokenizer(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    runner.unload()
    assert runner._model is None
    assert runner._tokenizer is None


# ── T386/T387: infer returns correct InferenceResult ─────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_infer_returns_inference_result_with_airllm_framework(
    mock_tok_cls, mock_airllm, config
):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    result = runner.infer("say hello", max_tokens=10)
    assert isinstance(result, InferenceResult)
    assert result.framework == "airllm"


# ── T398: prompt_token_count populated ───────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_infer_prompt_token_count_matches_mock_shape(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    result = runner.infer("prompt")
    assert result.prompt_token_count == _PROMPT_LEN


# ── T400: airllm_version in metadata ─────────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_infer_metadata_contains_airllm_version(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    result = runner.infer("hi")
    assert "airllm_version" in result.metadata


# ── T396: tokens_per_sec valid ────────────────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_infer_tokens_per_sec_is_non_negative_float(mock_tok_cls, mock_airllm, config):
    mock_airllm.from_pretrained.return_value = _mock_model(out_len=10)
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    result = runner.infer("hi")
    assert isinstance(result.tokens_per_sec, float)
    assert result.tokens_per_sec >= 0.0


# ── infer raises when no model loaded ────────────────────────────────────────


def test_infer_raises_runner_error_if_no_model_loaded(config):
    with pytest.raises(RunnerError, match="No model loaded"):
        _runner(config).infer("prompt")


# ── T395: tokenizer cached between calls ─────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_tokenizer_cached_between_successive_infer_calls(
    mock_tok_cls, mock_airllm, config
):
    mock_airllm.from_pretrained.return_value = _mock_model()
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    runner.infer("first call")
    runner.infer("second call")
    # from_pretrained for tokenizer must have been called exactly once (in load)
    mock_tok_cls.from_pretrained.assert_called_once()


# ── T393: gatekeeper wraps generate ──────────────────────────────────────────


@patch("hw5.services.airllm_runner._AirLLMAuto")
@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_gatekeeper_wraps_generate_call(mock_tok_cls, mock_airllm, config):
    mock_model = _mock_model()
    mock_airllm.from_pretrained.return_value = mock_model
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    gk = MagicMock(spec=ApiGatekeeper)
    gk.execute.side_effect = lambda fn, *a, **kw: fn(*a, **kw)
    runner = AirLLMRunner(config, gk)
    runner.load("some/model", QuantizationConfig.from_label("Q4"))
    runner.infer("hi")
    called_fns = [c.args[0] for c in gk.execute.call_args_list]
    assert mock_model.generate in called_fns


# ── T390: count_prompt_tokens ─────────────────────────────────────────────────


@patch("hw5.services.airllm_runner._AutoTokenizer")
def test_count_prompt_tokens_returns_positive_int(mock_tok_cls, config):
    mock_tok_cls.from_pretrained.return_value = _mock_tokenizer()
    runner = _runner(config)
    runner._model_id = "some/model"
    n = runner.count_prompt_tokens("hello world")
    assert isinstance(n, int)
    assert n > 0


# ── T399: RunnerProtocol structural duck-type check ──────────────────────────


def test_airllm_runner_has_all_protocol_methods(config):
    runner = _runner(config)
    for method in ("load", "infer", "unload", "health_check"):
        assert callable(getattr(runner, method, None)), f"missing method: {method}"
