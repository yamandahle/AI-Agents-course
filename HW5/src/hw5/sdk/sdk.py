"""EvalPipelineSDK — thin orchestration layer over the evaluation services."""

from __future__ import annotations

import logging
from pathlib import Path

from hw5.services.cell_persistence import load_existing_results
from hw5.services.cell_result import CellResult
from hw5.services.eval_loop import EvaluationLoop
from hw5.services.model_registry import ModelRegistry
from hw5.services.plotter import Plotter
from hw5.services.report import ReportGenerator
from hw5.services.summary import SummaryGenerator
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

log = logging.getLogger(__name__)


class EvalPipelineSDK:
    """High-level interface to the AirLLM vs Ollama evaluation pipeline."""

    def __init__(
        self,
        config_path: str = "config/setup.json",
        models_path: str | None = None,
    ) -> None:
        self._config = Config.load(config_path)
        self._gk = ApiGatekeeper()
        self._registry = ModelRegistry(self._gk)
        mp = models_path or str(Path(config_path).parent / "models.json")
        self._registry.load_config(mp)

    def run_full_evaluation(self) -> list[CellResult]:
        """Run all (model × framework × quant) cells and return results."""
        return EvaluationLoop(self._config, self._registry, self._gk).run()

    def run_single_cell(self, model: str, framework: str, quant: str) -> CellResult:
        """Run one evaluation cell by model name, framework, and quant label."""
        entry = self._registry.get_model(model)
        loop = EvaluationLoop(self._config, self._registry, self._gk)
        return loop.run_cell(entry, framework, QuantizationConfig.from_label(quant))

    def list_models(self) -> list[str]:
        """Return all registered model names, sorted alphabetically."""
        return self._registry.list_names()

    def get_results(self, results_dir: str | None = None) -> list[CellResult]:
        """Load all persisted CellResult JSONs from the results directory."""
        rdir = results_dir or self._config.results_dir
        return list(load_existing_results(rdir).values())

    def generate_plots(self, results: list[CellResult]) -> list[Path]:
        """Generate all four charts and return paths to all saved files."""
        return Plotter(results, self._config).save_all()

    def generate_summaries(self, results: list[CellResult]) -> dict[str, str]:
        """Generate prose summaries for all four chart sections."""
        return SummaryGenerator(results).generate_all()

    def generate_report(self, results: list[CellResult]) -> Path:
        """Generate and save the full HTML report; return its path."""
        summaries = self.generate_summaries(results)
        assets = Path(self._config.assets_dir)
        plot_paths = {
            f"{n}.png": assets / f"{n}.png"
            for n in ("heatmap", "ram_timeline", "vram_bar", "tradeoff_scatter")
        }
        gen = ReportGenerator(summaries, plot_paths, results)
        return gen.save(assets / "report.html")
