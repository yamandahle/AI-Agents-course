"""T436–T440: Unit tests for RunnerFactory."""

from __future__ import annotations

import pytest

from hw5.services.airllm_runner import AirLLMRunner
from hw5.services.ollama_runner import OllamaRunner
from hw5.services.runner_factory import RunnerFactory
from hw5.shared.gatekeeper import ApiGatekeeper


def _fast_gk() -> ApiGatekeeper:
    return ApiGatekeeper(rate=1000.0, burst=100)


# T436 — correct runner type returned per framework string


def test_factory_returns_ollama_runner_for_ollama(config):
    runner = RunnerFactory.create("ollama", config, _fast_gk())
    assert isinstance(runner, OllamaRunner)


def test_factory_returns_airllm_runner_for_airllm(config):
    runner = RunnerFactory.create("airllm", config, _fast_gk())
    assert isinstance(runner, AirLLMRunner)


# T437 — unknown framework raises ValueError


def test_factory_raises_for_unknown_framework(config):
    with pytest.raises(ValueError, match="Unknown framework"):
        RunnerFactory.create("vllm", config, _fast_gk())


# Verify returned runners have the expected protocol methods


def test_factory_ollama_runner_has_protocol_methods(config):
    runner = RunnerFactory.create("ollama", config, _fast_gk())
    for method in ("load", "infer", "unload", "health_check"):
        assert callable(getattr(runner, method, None))


def test_factory_airllm_runner_has_protocol_methods(config):
    runner = RunnerFactory.create("airllm", config, _fast_gk())
    for method in ("load", "infer", "unload", "health_check"):
        assert callable(getattr(runner, method, None))
