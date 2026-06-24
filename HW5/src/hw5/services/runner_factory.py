"""RunnerFactory — creates RunnerProtocol instances by framework name."""

from __future__ import annotations

from hw5.services.airllm_runner import AirLLMRunner
from hw5.services.ollama_runner import OllamaRunner
from hw5.services.runner_protocol import RunnerProtocol
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper


class RunnerFactory:
    """Maps a framework string to the correct RunnerProtocol implementation."""

    @staticmethod
    def create(
        framework: str,
        config: Config,
        gatekeeper: ApiGatekeeper,
    ) -> RunnerProtocol:
        """Return an OllamaRunner or AirLLMRunner for the given framework name."""
        if framework == "ollama":
            return OllamaRunner(config, gatekeeper)
        if framework == "airllm":
            return AirLLMRunner(config, gatekeeper)
        raise ValueError(
            f"Unknown framework '{framework}'. Supported: 'ollama', 'airllm'."
        )
