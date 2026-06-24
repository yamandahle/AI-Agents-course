"""Cell persistence — save and load CellResult JSON files to results_dir."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hw5.services.cell_result import CellResult

log = logging.getLogger(__name__)


def save_result(result: CellResult, results_dir: str) -> Path:
    """Write result to <results_dir>/cell_<cell_id>.json and return the path."""
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"cell_{result.cell_id}.json"
    if path.exists():
        log.debug("Result already saved at %s — skipping write", path)
        return path
    path.write_text(json.dumps(result.to_dict(), indent=2))
    log.info("Saved result → %s", path)
    return path


def load_existing_results(results_dir: str) -> dict[str, CellResult]:
    """Scan <results_dir> for cell_*.json files; return dict keyed by cell_id."""
    from hw5.services.cell_result import CellResult  # late import avoids circular

    out: dict[str, CellResult] = {}
    rdir = Path(results_dir)
    if not rdir.exists():
        return out
    for path in sorted(rdir.glob("cell_*.json")):
        try:
            cr = CellResult.from_dict(json.loads(path.read_text()))
            out[cr.cell_id] = cr
        except Exception as exc:
            log.warning("Skipping malformed result %s: %s", path.name, exc)
    return out
