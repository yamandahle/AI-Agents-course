"""EvaluationLoop — orchestrates all (model × framework × quant) cells."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from hw5.services.cell_persistence import load_existing_results, save_result
from hw5.services.cell_result import CellResult
from hw5.services.model_entry import ModelEntry
from hw5.services.monitor import SystemMonitor
from hw5.services.runner_factory import RunnerFactory
from hw5.services.runner_protocol import InferenceResult
from hw5.shared.config import Config
from hw5.shared.gatekeeper import ApiGatekeeper
from hw5.shared.quant_config import QuantizationConfig

log = logging.getLogger(__name__)


class EvaluationLoop:
    """Runs every (model, framework, quant) cell and persists each CellResult."""

    def __init__(
        self,
        config: Config,
        registry,  # ModelRegistry — avoid circular import
        gatekeeper: ApiGatekeeper,
    ) -> None:
        self._config = config
        self._registry = registry
        self._gatekeeper = gatekeeper

    def iter_cells(self) -> Iterator[tuple[ModelEntry, str, QuantizationConfig]]:
        """Yield (model_entry, framework, quant_config) for every runnable cell."""
        for entry in self._registry.list_models():
            for fw in self._config.frameworks:
                if fw == "ollama" and not entry.ollama_compatible:
                    continue
                if fw == "airllm" and not entry.airllm_compatible:
                    continue
                for label in self._config.quantization_levels:
                    yield entry, fw, QuantizationConfig.from_label(label)

    def run(self) -> list[CellResult]:
        """Run all pending cells; skip completed ones when config.resume is True."""
        cells = list(self.iter_cells())
        done: dict[str, CellResult] = {}
        if self._config.resume:
            done = load_existing_results(self._config.results_dir)
            log.info(
                "Resuming: %d done, %d remaining", len(done), len(cells) - len(done)
            )
        results: list[CellResult] = list(done.values())
        pending = [
            (e, fw, q) for e, fw, q in cells if f"{e.name}__{fw}__{q}" not in done
        ]
        cols = (SpinnerColumn(), TextColumn("{task.description}"), TimeElapsedColumn())
        with Progress(*cols) as prog:
            task = prog.add_task("Evaluating", total=len(pending))
            for entry, fw, quant in pending:
                prog.update(task, description=f"{entry.name}__{fw}__{quant}")
                results.append(self.run_cell(entry, fw, quant))
                prog.advance(task)
        log.info(
            "Done: %d cells, %d failed",
            len(results),
            sum(1 for r in results if r.failed),
        )
        return results

    def run_cell(
        self, entry: ModelEntry, framework: str, quant: QuantizationConfig
    ) -> CellResult:
        """Run one evaluation cell, catch any exception, and return a CellResult."""
        cell_id = f"{entry.name}__{framework}__{quant}"
        model_id = (
            entry.ollama_tag_for(quant.label)
            if framework == "ollama"
            else entry.hf_repo_id
        )
        runner = RunnerFactory.create(framework, self._config, self._gatekeeper)
        monitor = SystemMonitor(self._config)
        t0 = time.perf_counter()
        monitor.start()
        infer_result: InferenceResult | None = None
        failed, error_msg = False, ""
        try:
            runner.load(model_id, quant)
            infer_result = runner.infer(
                self._config.eval_prompt, self._config.max_tokens
            )
            runner.unload()
        except Exception as exc:
            failed, error_msg = True, str(exc)
            log.error("Cell %s FAILED: %s", cell_id, exc)
            try:
                runner.unload()
            except Exception:
                pass
        finally:
            snap = monitor.stop()
        t1 = time.perf_counter()
        if infer_result is None:
            infer_result = InferenceResult(
                output_text="",
                tokens_generated=0,
                total_time_s=0.0,
                first_token_latency_s=0.0,
                framework=framework,
                model_id=model_id,
                quant=str(quant),
            )
        result = CellResult(
            cell_id=cell_id,
            inference=infer_result,
            metrics=snap,
            started_at=t0,
            finished_at=t1,
            cpu_only=self._config.cpu_only_mode,
            failed=failed,
            error_message=error_msg,
        )
        save_result(result, self._config.results_dir)
        return result

    def get_successful_results(self, results: list[CellResult]) -> list[CellResult]:
        """Return only the non-failed cells from a results list."""
        return [r for r in results if not r.failed]

    def filter_cells(
        self,
        models: list[str] | None = None,
        frameworks: list[str] | None = None,
        quants: list[str] | None = None,
    ) -> list[tuple[ModelEntry, str, QuantizationConfig]]:
        """Return the subset of iter_cells() matching the provided filters."""
        cells = list(self.iter_cells())
        if models:
            cells = [(e, fw, q) for e, fw, q in cells if e.name in models]
        if frameworks:
            cells = [(e, fw, q) for e, fw, q in cells if fw in frameworks]
        if quants:
            cells = [(e, fw, q) for e, fw, q in cells if str(q) in quants]
        return cells
