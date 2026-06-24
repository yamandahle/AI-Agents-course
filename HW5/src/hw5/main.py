"""CLI entry point — AirLLM vs Ollama evaluation pipeline."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from hw5.sdk.sdk import EvalPipelineSDK
from hw5.services.eval_loop import EvaluationLoop

log = logging.getLogger(__name__)

_MODES = ["full", "single", "plot", "report"]
_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hw5",
        description="AirLLM vs Ollama local LLM evaluation pipeline",
    )
    p.add_argument("--mode", choices=_MODES, default="full", help="execution mode")
    p.add_argument("--config", default="config/setup.json", help="path to setup.json")
    p.add_argument("--cell", metavar="CELL_ID", help="cell for --mode single")
    p.add_argument("--resume", action="store_true", help="skip existing results")
    p.add_argument("--models", metavar="M1,M2", help="comma-sep model names")
    p.add_argument("--frameworks", metavar="F1,F2", help="comma-sep frameworks")
    p.add_argument("--quants", metavar="Q1,Q2", help="comma-sep quant levels")
    p.add_argument("--dry-run", action="store_true", help="list cells no execute")
    p.add_argument("--live", action="store_true", help="show real-time metrics")
    p.add_argument("--log-level", choices=_LOG_LEVELS, default="INFO", dest="log_level")
    p.add_argument("--output-dir", metavar="DIR", help="redirect results/assets")
    p.add_argument("--eval-prompt", metavar="PROMPT", help="override eval prompt")
    p.add_argument("--max-tokens", type=int, metavar="N", help="override max_tokens")
    return p


def _apply_overrides(sdk: EvalPipelineSDK, args: argparse.Namespace) -> None:
    cfg = sdk._config
    if args.resume:
        cfg.resume = True
    if args.output_dir:
        cfg.results_dir = str(Path(args.output_dir) / "results")
        cfg.assets_dir = str(Path(args.output_dir) / "assets")
    if args.eval_prompt:
        cfg.eval_prompt = args.eval_prompt
    if args.max_tokens:
        cfg.max_tokens = args.max_tokens


def _dry_run(sdk: EvalPipelineSDK, args: argparse.Namespace) -> None:
    loop = EvaluationLoop(sdk._config, sdk._registry, sdk._gk)
    models = args.models.split(",") if args.models else None
    frameworks = args.frameworks.split(",") if args.frameworks else None
    quants = args.quants.split(",") if args.quants else None
    cells = loop.filter_cells(models=models, frameworks=frameworks, quants=quants)
    print(f"[dry-run] {len(cells)} cell(s) would run:")
    for entry, fw, quant in cells:
        print(f"  {entry.name}__{fw}__{quant}")


def main(argv: list[str] | None = None) -> int:
    """Parse CLI args, dispatch to the correct mode, and return exit code."""
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    sdk = EvalPipelineSDK(config_path=args.config)
    _apply_overrides(sdk, args)

    if args.dry_run:
        _dry_run(sdk, args)
        return 0

    failed_count = 0

    if args.mode == "full":
        results = sdk.run_full_evaluation()
        failed_count = sum(1 for r in results if r.failed)
        print(f"Completed {len(results)} cell(s), {failed_count} failed.")

    elif args.mode == "single":
        if not args.cell:
            print("--cell CELL_ID is required for --mode single", file=sys.stderr)
            return 1
        parts = args.cell.split("__")
        if len(parts) != 3:
            print("--cell must be model__framework__quant", file=sys.stderr)
            return 1
        result = sdk.run_single_cell(*parts)
        failed_count = 1 if result.failed else 0
        print(f"Cell {result.cell_id}: {'FAILED' if result.failed else 'OK'}")

    elif args.mode == "plot":
        results = sdk.get_results()
        paths = sdk.generate_plots(results)
        print(f"Saved {len(paths)} plot file(s).")

    elif args.mode == "report":
        results = sdk.get_results()
        path = sdk.generate_report(results)
        print(f"Report saved → {path}")

    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
