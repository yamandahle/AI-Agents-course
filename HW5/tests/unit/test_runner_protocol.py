"""T105–T108: Tests for InferenceResult and RunnerProtocol."""

from __future__ import annotations

import pytest

from hw5.services.runner_protocol import InferenceResult, RunnerProtocol
from hw5.shared.quant_config import QuantizationConfig


def _make_result(**overrides) -> InferenceResult:
    defaults = dict(
        output_text="hello world",
        tokens_generated=10,
        total_time_s=2.0,
        first_token_latency_s=0.3,
        framework="ollama",
        model_id="test/model",
        quant="Q4",
    )
    defaults.update(overrides)
    return InferenceResult(**defaults)


# T107 — to_dict / from_dict roundtrip
def test_to_dict_contains_all_fields():
    r = _make_result()
    d = r.to_dict()
    assert d["output_text"] == "hello world"
    assert d["tokens_generated"] == 10
    assert d["framework"] == "ollama"
    assert d["quant"] == "Q4"
    assert "tokens_per_sec" in d
    assert "metadata" in d


def test_from_dict_roundtrip():
    r = _make_result(prompt_token_count=5, metadata={"key": "val"})
    d = r.to_dict()
    r2 = InferenceResult.from_dict(d)
    assert r2.output_text == r.output_text
    assert r2.tokens_generated == r.tokens_generated
    assert r2.framework == r.framework
    assert r2.metadata == {"key": "val"}
    assert r2.prompt_token_count == 5


def test_from_dict_with_missing_optional_fields():
    d = {
        "output_text": "hi",
        "tokens_generated": 3,
        "total_time_s": 1.0,
        "first_token_latency_s": 0.1,
        "framework": "airllm",
        "model_id": "m",
        "quant": "Q8",
    }
    r = InferenceResult.from_dict(d)
    assert r.prompt_token_count == 0
    assert r.tokens_per_sec == pytest.approx(3.0)
    assert r.metadata == {}


# T108 — tokens_per_sec auto-computed
def test_tokens_per_sec_auto_computed_when_zero():
    r = _make_result(tokens_generated=20, total_time_s=4.0, tokens_per_sec=0.0)
    assert r.tokens_per_sec == pytest.approx(5.0)


def test_tokens_per_sec_not_overwritten_when_provided():
    r = _make_result(tokens_generated=20, total_time_s=4.0, tokens_per_sec=99.0)
    assert r.tokens_per_sec == pytest.approx(99.0)


def test_tokens_per_sec_zero_when_time_is_zero():
    r = _make_result(tokens_generated=10, total_time_s=0.0, tokens_per_sec=0.0)
    assert r.tokens_per_sec == pytest.approx(0.0)


# T105/T106 — structural protocol compliance via a concrete stub
class _StubRunner:
    """Minimal concrete runner satisfying RunnerProtocol for structural check."""

    def load(self, model_id: str, quant: QuantizationConfig) -> None:
        pass

    def infer(self, prompt: str, max_tokens: int) -> InferenceResult:
        return _make_result()

    def unload(self) -> None:
        pass

    def health_check(self) -> bool:
        return True


def test_stub_runner_satisfies_protocol():
    runner: RunnerProtocol = _StubRunner()  # type: ignore[assignment]
    assert runner.health_check() is True
    result = runner.infer("hello", 50)
    assert isinstance(result, InferenceResult)


def test_stub_runner_load_and_unload():
    runner = _StubRunner()
    runner.load("org/model", QuantizationConfig.from_label("Q4"))
    runner.unload()


def test_inference_result_metadata_is_mutable():
    r = _make_result()
    r.metadata["layer_count"] = 32
    assert r.metadata["layer_count"] == 32


def test_inference_result_framework_stored():
    r = _make_result(framework="airllm")
    assert r.framework == "airllm"
