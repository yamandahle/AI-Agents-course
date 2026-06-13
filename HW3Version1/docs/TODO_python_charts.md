# TODO — Python-First Chart Generation Pipeline

## Phase 1 — Chart generator
- [ ] C1. Create `src/article_writer/tools/chart_generator.py`
- [ ] C2. Implement `generate_accuracy_curve(out_dir: Path) -> Path`
- [ ] C3. Implement `generate_diagnostic_comparison(out_dir: Path) -> Path`
- [ ] C4. Implement `generate_cost_reduction(out_dir: Path) -> Path`
- [ ] C5. Implement `generate_all(out_dir: Path) -> list[Path]` (skips existing)
- [ ] C6. Run standalone to verify all 3 PDFs are created

## Phase 2 — Sanitizer
- [ ] S1. Add `tex_dir: Path | None = None` param to `_fix_includegraphics`
- [ ] S2. Inside `_replace()` add file-existence check before replacement
- [ ] S3. Update `sanitize()` to pass `tex_path.parent` as `tex_dir`
- [ ] S4. Verify ruff passes after change

## Phase 3 — Draft prompt
- [ ] P1. Remove "Do NOT use \includegraphics at all" from line ~69 in _draft_prompt.py
- [ ] P2. Replace with "PRE-GENERATED CHARTS" block listing 3 paths + descriptions
- [ ] P3. Remove the duplicate hard-rule "NO \includegraphics for charts" from HARD RULES
- [ ] P4. Keep logo \includegraphics instruction unchanged

## Phase 4 — SDK wiring
- [ ] K1. Import `generate_all` from `chart_generator` in `sdk.py`
- [ ] K2. Call `generate_all(Path("assets/graphs"))` at start of `start_writing_session`

## Phase 5 — Tests
- [ ] T1. Add `test_fix_includegraphics_skips_when_pdf_exists` to sanitizer_extra.py
- [ ] T2. Add `test_fix_includegraphics_replaces_when_pdf_missing` to sanitizer_extra.py
- [ ] T3. Add tests for `chart_generator.py` in `tests/unit/test_tools/test_chart_generator.py`

## Verification
- [ ] V1. `uv run ruff check src/` → 0 violations
- [ ] V2. `uv run pytest tests/ --cov-fail-under=85` → all pass
- [ ] V3. Run `generate_all` standalone → 3 PDFs in assets/graphs/
- [ ] V4. Compile `results/draft_final.tex` (has accuracy_curve) → PDF builds clean
- [ ] V5. git commit + push
