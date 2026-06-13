# PRD — Python-First Chart Generation Pipeline

## Problem
The current pipeline instructs the LLM to generate pgfplots/TikZ code for charts
directly inside the LaTeX draft. This is fragile: the LLM frequently produces broken
axis environments, mismatched coordinates, or undefined styles that require a 12-step
sanitizer to repair — and still occasionally fail at compile time.

## Goal
Replace LLM-generated pgfplots charts with pre-generated Python/matplotlib PDFs that
the LLM simply references via `\includegraphics`. Charts are always clean, always
present on disk before the LLM runs, and never touch the sanitizer.

## Requirements

### R1 — Chart generator script
`assets/graphs/generate_all_charts.py` generates three publication-quality PDFs:
- `accuracy_curve.pdf` — training vs validation accuracy over epochs
- `diagnostic_comparison.pdf` — AI vs human accuracy on 5 medical imaging tasks (bar)
- `cost_reduction.pdf` — operational cost savings with AI agents (horizontal bar)

Script is callable standalone (`uv run python assets/graphs/generate_all_charts.py`)
and as a library (`from generate_all_charts import generate_all`).

### R2 — Sanitizer: skip existing images
`LatexSanitizer._fix_includegraphics` receives the tex file directory and checks
whether the referenced PDF exists on disk. If it does, the block is kept as-is.
Only missing or non-PDF `\includegraphics` references are replaced with pgfplots.

Signature change:
```python
def _fix_includegraphics(self, source: str, tex_dir: Path | None = None) -> tuple[str, int]
```

`sanitize(tex_path)` passes `tex_path.parent` as `tex_dir`.

### R3 — Draft prompt: use \includegraphics for charts
Remove the "Do NOT use \includegraphics for charts" instruction.
Add a "Pre-generated charts" block listing the three PDFs with descriptions,
telling the LLM to reference them instead of writing pgfplots code.
The logo `\includegraphics` (uniHaifasymbol.png) is unchanged.

### R4 — SDK: generate charts before draft
`ArticleWriterSDK.start_writing_session` calls `generate_all_charts()` before
`DraftGenerator.generate()` so PDFs always exist when the LLM runs.

### R5 — Tests
- New `test_latex_sanitizer_extra.py` test: sanitizer skips `\includegraphics` when
  the referenced PDF exists on disk.
- New test: sanitizer still replaces `\includegraphics` when the file is missing.
- Existing tests remain green.

## Out of scope
- Dynamic chart data from research.md (static curated values only)
- Chart regeneration on every pipeline run (idempotent — skip if exists)
- Changing the TikZ flow-diagram path (still LLM-generated, sanitizer handles it)
