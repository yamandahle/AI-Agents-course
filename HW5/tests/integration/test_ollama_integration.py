"""T315–T320: Integration tests for OllamaRunner — requires running Ollama server."""

from __future__ import annotations

import shutil

import pytest

from hw5.services.ollama_runner import OllamaRunner
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

pytestmark = pytest.mark.integration

_OLLAMA_AVAILABLE = bool(shutil.which("ollama"))
_SKIP = pytest.mark.skipif(not _OLLAMA_AVAILABLE, reason="ollama binary not installed")

_TEST_MODEL = "qwen2.5:1.5b-instruct-q4_K_M"


@_SKIP
def test_health_check_returns_true_with_running_server(config: Config):
    gk = ApiGatekeeper(rate=2.0, burst=5)
    runner = OllamaRunner(config, gk)
    assert runner.health_check() is True


@_SKIP
def test_pull_and_infer_produces_non_empty_output(config: Config):
    gk = ApiGatekeeper(rate=2.0, burst=5)
    runner = OllamaRunner(config, gk)
    quant = QuantizationConfig.from_label("Q4")
    runner.load(_TEST_MODEL, quant)
    result = runner.infer("Reply with one word: yes or no?", max_tokens=10)
    assert len(result.output_text.strip()) > 0
    runner.unload()


@_SKIP
def test_first_token_latency_is_positive(config: Config):
    gk = ApiGatekeeper(rate=2.0, burst=5)
    runner = OllamaRunner(config, gk)
    quant = QuantizationConfig.from_label("Q4")
    runner.load(_TEST_MODEL, quant)
    result = runner.infer("Hello", max_tokens=5)
    assert result.first_token_latency_s > 0.0
    runner.unload()
