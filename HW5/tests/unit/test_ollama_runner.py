"""T294–T310: Unit tests for OllamaRunner (all ollama calls mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hw5.services.ollama_runner import OllamaRunner, RunnerError
from hw5.services.runner_protocol import InferenceResult
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

# ── helpers ───────────────────────────────────────────────────────────────────


def _chunk(text: str = "", done: bool = False, eval_count: int = 0) -> MagicMock:
    c = MagicMock()
    c.response = text
    c.done = done
    c.eval_count = eval_count
    return c


def _fast_gk() -> ApiGatekeeper:
    return ApiGatekeeper(rate=1000.0, burst=100)


def _runner(config) -> OllamaRunner:
    return OllamaRunner(config, _fast_gk())


# ── T295/T296: health_check ───────────────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_health_check_true_when_server_responds(mock_ol, config):
    mock_ol.list.return_value = []
    runner = _runner(config)
    assert runner.health_check() is True


@patch("hw5.services.ollama_runner._ollama")
def test_health_check_false_on_connection_error(mock_ol, config):
    mock_ol.list.side_effect = Exception("connection refused")
    runner = _runner(config)
    assert runner.health_check() is False


# ── T297/T298: load ───────────────────────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_load_calls_pull_with_resolved_tag(mock_ol, config):
    mock_ol.list.return_value = []
    runner = _runner(config)
    quant = QuantizationConfig.from_label("Q4")
    runner.load("qwen2.5:7b-instruct-q4_K_M", quant)
    mock_ol.pull.assert_called_once_with("qwen2.5:7b-instruct-q4_K_M")


@patch("hw5.services.ollama_runner._ollama")
def test_load_raises_runner_error_when_server_not_healthy(mock_ol, config):
    mock_ol.list.side_effect = Exception("not running")
    runner = _runner(config)
    with pytest.raises(RunnerError, match="not reachable"):
        runner.load("qwen2.5:7b-instruct-q4_K_M", QuantizationConfig.from_label("Q4"))


# ── T302: _resolve_tag ────────────────────────────────────────────────────────


def test_resolve_tag_returns_existing_ollama_tag(config):
    runner = _runner(config)
    quant = QuantizationConfig.from_label("Q4")
    tag = runner._resolve_tag("qwen2.5:7b-instruct-q4_K_M", quant)
    assert tag == "qwen2.5:7b-instruct-q4_K_M"


def test_resolve_tag_constructs_from_hf_repo_id(config):
    runner = _runner(config)
    quant = QuantizationConfig.from_label("Q4")
    tag = runner._resolve_tag("Qwen/Qwen2.5-7B-Instruct", quant)
    assert "qwen2.5-7b-instruct" in tag
    assert "q4" in tag.lower()


# ── T303/T299/T300/T309/T310: infer ──────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_infer_accumulates_streaming_text(mock_ol, config):
    mock_ol.list.return_value = []
    chunks = [_chunk("Hello"), _chunk(" world"), _chunk("", done=True, eval_count=5)]
    mock_ol.generate.return_value = iter(chunks)

    runner = _runner(config)
    quant = QuantizationConfig.from_label("Q4")
    runner.load("model:tag", quant)
    result = runner.infer("say hi")

    assert result.output_text == "Hello world"


@patch("hw5.services.ollama_runner._ollama")
def test_infer_captures_first_token_latency(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.generate.return_value = iter(
        [
            _chunk("tok1"),
            _chunk("", done=True, eval_count=2),
        ]
    )
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    result = runner.infer("prompt")
    assert result.first_token_latency_s >= 0.0


@patch("hw5.services.ollama_runner._ollama")
def test_infer_extracts_token_count_from_eval_count(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.generate.return_value = iter(
        [
            _chunk("tok"),
            _chunk("", done=True, eval_count=42),
        ]
    )
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    result = runner.infer("prompt")
    assert result.tokens_generated == 42


@patch("hw5.services.ollama_runner._ollama")
def test_infer_tokens_per_sec_positive(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.generate.return_value = iter(
        [
            _chunk("text"),
            _chunk("", done=True, eval_count=10),
        ]
    )
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    result = runner.infer("prompt")
    assert isinstance(result.tokens_per_sec, float)
    assert result.tokens_per_sec >= 0.0


@patch("hw5.services.ollama_runner._ollama")
def test_infer_framework_field_is_ollama(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.generate.return_value = iter([_chunk("hi", done=True, eval_count=1)])
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    result = runner.infer("hi")
    assert result.framework == "ollama"


# ── T304: error handling ──────────────────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_infer_raises_runner_error_on_ollama_exception(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.generate.side_effect = RuntimeError("server crash")
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    with pytest.raises(RunnerError, match="Inference failed"):
        runner.infer("prompt")


# ── T308: no model loaded ─────────────────────────────────────────────────────


def test_infer_raises_runner_error_if_no_model_loaded(config):
    runner = _runner(config)
    with pytest.raises(RunnerError, match="No model loaded"):
        runner.infer("prompt")


# ── T301: unload ─────────────────────────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_unload_calls_delete_with_current_tag(mock_ol, config):
    mock_ol.list.return_value = []
    runner = _runner(config)
    quant = QuantizationConfig.from_label("Q4")
    runner.load("model:tag", quant)
    runner.unload()
    mock_ol.delete.assert_called_once_with("model:tag")
    assert runner._current_tag is None


# ── T306: get_model_info ──────────────────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_get_model_info_returns_dict(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.show.return_value = {"modelfile": "FROM qwen2.5"}
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    info = runner.get_model_info()
    assert isinstance(info, dict)


def test_get_model_info_empty_when_no_model_loaded(config):
    runner = _runner(config)
    assert runner.get_model_info() == {}


# ── T307: gatekeeper wraps generate ──────────────────────────────────────────


def test_gatekeeper_called_for_generate(config):
    gk = MagicMock(spec=ApiGatekeeper)
    gk.execute.side_effect = lambda fn, *a, **kw: fn(*a, **kw)
    runner = OllamaRunner(config, gk)

    with patch("hw5.services.ollama_runner._ollama") as mock_ol:
        mock_ol.list.return_value = []
        mock_ol.generate.return_value = iter([_chunk("hi", done=True, eval_count=1)])
        runner.load("model:tag", QuantizationConfig.from_label("Q4"))
        runner.infer("prompt")

    call_fns = [call.args[0] for call in gk.execute.call_args_list]
    assert mock_ol.generate in call_fns


# ── T294: InferenceResult structure ──────────────────────────────────────────


@patch("hw5.services.ollama_runner._ollama")
def test_infer_result_has_all_required_fields(mock_ol, config):
    mock_ol.list.return_value = []
    mock_ol.generate.return_value = iter([_chunk("answer", done=True, eval_count=3)])
    runner = _runner(config)
    runner.load("model:tag", QuantizationConfig.from_label("Q4"))
    result = runner.infer("question")
    assert isinstance(result, InferenceResult)
    assert result.output_text == "answer"
    assert result.total_time_s >= 0.0
    assert result.model_id == "model:tag"
    assert result.quant == "Q4"
