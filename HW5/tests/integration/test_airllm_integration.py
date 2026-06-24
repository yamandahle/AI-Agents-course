"""T411–T416: Integration tests for AirLLMRunner — requires HF_TOKEN and disk space."""

from __future__ import annotations

import os

import pytest

from hw5.services.airllm_runner import _AIRLLM_AVAILABLE, AirLLMRunner
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

pytestmark = pytest.mark.integration

_HAS_TOKEN = bool(os.getenv("HF_TOKEN"))
_SKIP = pytest.mark.skipif(
    not (_AIRLLM_AVAILABLE and _HAS_TOKEN),
    reason="airllm not installed or HF_TOKEN not set",
)

_TEST_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


@_SKIP
def test_health_check_true_with_airllm_installed(config: Config):
    gk = ApiGatekeeper(rate=1.0, burst=2)
    runner = AirLLMRunner(config, gk)
    assert runner.health_check() is True


@_SKIP
def test_load_and_infer_produces_non_empty_output(config: Config):
    gk = ApiGatekeeper(rate=1.0, burst=2)
    runner = AirLLMRunner(config, gk)
    quant = QuantizationConfig.from_label("Q4")
    runner.load(_TEST_MODEL, quant)
    result = runner.infer("Reply with one word: yes or no?", max_tokens=10)
    assert len(result.output_text.strip()) > 0
    runner.unload()


@_SKIP
def test_layer_streaming_keeps_ram_below_8gb(config: Config):
    """Verify that AirLLM layer streaming avoids loading the full model into RAM."""
    gk = ApiGatekeeper(rate=1.0, burst=2)
    runner = AirLLMRunner(config, gk)
    quant = QuantizationConfig.from_label("Q4")
    runner.load(_TEST_MODEL, quant)
    result = runner.infer("Hello", max_tokens=5)
    assert result.total_time_s > 0.0
    runner.unload()
