# PLAN — Python-First Chart Generation Pipeline

## Phase 1 — Chart generator (no touching existing code)
Create `assets/graphs/generate_all_charts.py`.
- `generate_accuracy_curve(out_dir)` → `accuracy_curve.pdf`
- `generate_diagnostic_comparison(out_dir)` → `diagnostic_comparison.pdf`
- `generate_cost_reduction(out_dir)` → `cost_reduction.pdf`
- `generate_all(out_dir)` calls all three, skips if file already exists
- `if __name__ == "__main__": generate_all(Path("assets/graphs"))` for standalone use

All charts: figsize 8×5, tight_layout, Agg backend, saved as PDF.

## Phase 2 — Sanitizer: file-existence check (1 file, 3 lines changed)
File: `src/article_writer/latex/latex_sanitizer.py`

Change `_fix_includegraphics` signature to accept `tex_dir: Path | None = None`.
Inside `_replace()`, before deciding to swap:
```python
if tex_dir is not None:
    candidate = (tex_dir / ig.group(1)).resolve()
    if candidate.exists():
        return block   # file present — keep \includegraphics as-is
```
Update `sanitize()` to pass `tex_path.parent`:
```python
s, n3 = self._fix_includegraphics(s, tex_dir=tex_path.parent)
```

## Phase 3 — Draft prompt update (1 file)
File: `src/article_writer/writing/_draft_prompt.py`

Replace the block:
```
Do NOT use \includegraphics at all — it requires external files that do not exist.
For charts, use pgfplots.
```
With:
```
PRE-GENERATED CHARTS — use \includegraphics for these (files exist on disk):
  \includegraphics[width=0.88\textwidth]{../assets/graphs/accuracy_curve.pdf}
    → Training vs validation accuracy over epochs (deep learning model)
  \includegraphics[width=0.88\textwidth]{../assets/graphs/diagnostic_comparison.pdf}
    → AI vs human diagnostic accuracy on 5 medical imaging tasks (bar chart)
  \includegraphics[width=0.88\textwidth]{../assets/graphs/cost_reduction.pdf}
    → Operational cost reduction with AI agents across hospital departments
Use each chart exactly once, inside \begin{figure}[H]...\end{figure} with \caption and \label.
For flow diagrams (not data charts) still use tikzpicture.
```
Also remove the hard-rule line "Do NOT use \includegraphics at all" from HARD RULES.

## Phase 4 — SDK wiring (1 file, ~5 lines)
File: `src/article_writer/sdk/sdk.py`

Add import at top of `start_writing_session`:
```python
from assets.graphs.generate_all_charts import generate_all  # noqa
```
Wait — `assets/` is not a Python package. Use subprocess or importlib instead:
```python
import subprocess, sys
subprocess.run([sys.executable, "assets/graphs/generate_all_charts.py"], check=True)
```
Or better: add `generate_all_charts.py` as a module under `src/article_writer/tools/`
and import it from there. This keeps it inside the package.

**Decision**: copy logic into `src/article_writer/tools/chart_generator.py` (new file).
`generate_all(out_dir: Path) → list[Path]` — generates missing charts, returns paths.
`sdk.start_writing_session` imports and calls it before `DraftGenerator`.

## Phase 5 — Tests (2 new test cases in existing file)
File: `tests/unit/test_latex/test_latex_sanitizer_extra.py`

Add:
- `test_fix_includegraphics_skips_when_pdf_exists(tmp_path)`:
  write a dummy PDF to `tmp_path/assets/graphs/chart.pdf`,
  call `_fix_includegraphics(src, tex_dir=tmp_path/"results")`, assert n == 0.
- `test_fix_includegraphics_replaces_when_pdf_missing(tmp_path)`:
  call with `tex_dir` pointing to empty dir, assert n > 0.

## Execution order
1 → 2 → 3 → 4 → 5 → run tests → run ruff → commit
