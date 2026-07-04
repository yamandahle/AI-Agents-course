"""CLI: run experiment cases and build summary + graphs."""

import argparse
import json
import logging
import subprocess
import sys

from cop_thief.experiments.cases import EXPERIMENT_CASES, case_names, load_case_config
from cop_thief.experiments.graphs import generate_all
from cop_thief.experiments.metrics import collect, save, write_summary_csv
from cop_thief.shared.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse experiment runner CLI flags."""
    parser = argparse.ArgumentParser(description="Cop & Thief experiment runner")
    parser.add_argument("--case", help="Run one case by name")
    parser.add_argument("--all", action="store_true", help="Run all 3 cases")
    parser.add_argument(
        "--graphs-only",
        action="store_true",
        help="Build summary.csv + graphs from existing result.json files",
    )
    parser.add_argument("--gui", action="store_true", help="Enable GUI during runs")
    return parser.parse_args(argv)


def _run_main_py(config_file: str, gui: bool) -> None:
    """Delegate one game run to src/main.py (avoids duplicating server wiring)."""
    cmd = ["uv", "run", "python", "src/main.py", "--config", config_file]
    cmd.append("--gui" if gui else "--headless")
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def _load_result(case_name: str) -> dict | None:
    """Read results/<case>/result.json if it exists."""
    path = PROJECT_ROOT / "results" / case_name / "result.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _build_metrics_for_case(case_name: str) -> dict | None:
    """Collect metrics for one case from its saved result.json."""
    result = _load_result(case_name)
    if result is None:
        logger.warning("Missing result for %s — skip metrics", case_name)
        return None
    config = load_case_config(case_name)
    meta = EXPERIMENT_CASES[case_name]
    metrics = collect(result, case_name, config, meta["grid_label"])
    save(metrics, PROJECT_ROOT / "results")
    return metrics


def build_summary_and_graphs() -> None:
    """Aggregate metrics from all cases that have results; write charts."""
    results_dir = PROJECT_ROOT / "results"
    all_metrics = [
        m for name in case_names() if (m := _build_metrics_for_case(name)) is not None
    ]
    if not all_metrics:
        raise FileNotFoundError("No result.json files found under results/")
    summary_path = write_summary_csv(all_metrics, results_dir)
    graph_dir = results_dir / "graphs"
    paths = generate_all(summary_path, results_dir, graph_dir)
    logger.info("Wrote %s and %d graphs", summary_path, len(paths))


def main(argv: list[str] | None = None) -> None:
    """Entry point for python -m cop_thief.experiments.runner."""
    logging.basicConfig(level=logging.INFO)
    args = _parse_args(argv)

    if args.graphs_only:
        build_summary_and_graphs()
        return

    names = case_names() if args.all else [args.case] if args.case else []
    if not names:
        print("Specify --case <name>, --all, or --graphs-only", file=sys.stderr)
        sys.exit(1)

    for name in names:
        config_file = EXPERIMENT_CASES[name]["config_file"]
        logger.info("Running experiment %s", name)
        _run_main_py(config_file, gui=args.gui)

    build_summary_and_graphs()


if __name__ == "__main__":
    main()
