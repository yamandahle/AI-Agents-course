"""Services layer: runners, monitor, evaluator, plotter, and summary."""

from hw5.services.airllm_runner import AirLLMRunner, UnsupportedQuantError
from hw5.services.cell_persistence import load_existing_results, save_result
from hw5.services.cell_result import CellResult
from hw5.services.eval_loop import EvaluationLoop
from hw5.services.metrics_buffer import MetricsBuffer, VRAMSpikeEvent
from hw5.services.metrics_snapshot import MetricsSnapshot
from hw5.services.model_entry import ModelEntry
from hw5.services.model_registry import DownloadError, ModelRegistry, RegistryError
from hw5.services.monitor import SystemMonitor
from hw5.services.ollama_runner import OllamaRunner, RunnerError
from hw5.services.plotter import Plotter
from hw5.services.report import ReportGenerator
from hw5.services.runner_factory import RunnerFactory
from hw5.services.runner_protocol import InferenceResult, RunnerProtocol
from hw5.services.summary import SummaryGenerator

__all__ = [
    "InferenceResult",
    "RunnerProtocol",
    "ModelEntry",
    "ModelRegistry",
    "RegistryError",
    "DownloadError",
    "MetricsBuffer",
    "VRAMSpikeEvent",
    "MetricsSnapshot",
    "SystemMonitor",
    "OllamaRunner",
    "RunnerError",
    "AirLLMRunner",
    "UnsupportedQuantError",
    "RunnerFactory",
    "CellResult",
    "load_existing_results",
    "save_result",
    "EvaluationLoop",
    "Plotter",
    "SummaryGenerator",
    "ReportGenerator",
]
