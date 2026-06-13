# TODO — TikZ Spatial Collision Prevention

## Phase 1 — Writer prompt
- [ ] W1. Add TIKZ FLOWCHART RULES block to `_draft_prompt.py` §2b (after pgfplots example)
- [ ] W2. Strengthen HARD RULES ARROW LABELS entry: forbid bare `--` on multi-hop paths

## Phase 2 — Reviewer prompt
- [ ] R1. Add `TikzLayout` priority item 3 to `_REVIEWER_SYSTEM` in `reviewer.py`
- [ ] R2. Add two explicit rejection criteria (missing fill=white, diagonal crossing)
- [ ] R3. Add "TikzLayout" to allowed profile values in reviewer docstring

## Phase 3 — Editor prompt
- [ ] E1. Add TikZ collision fix as priority 2 in `_EDITOR_SYSTEM` in `editor.py`
- [ ] E2. Add `"TikzLayout"` to `priority_order` list in `_format_comments`

## Phase 4 — Sanitizer
- [ ] S1. Implement `_fix_diagonal_paths()` in `latex_sanitizer.py`
- [ ] S2. Wire `_fix_diagonal_paths` into `sanitize()` as Fix 12 (n12)
- [ ] S3. Update sanitize() log line to include n12

## Phase 5 — Tests
- [ ] T1. `test_fix_diagonal_paths_converts_diagonal`
- [ ] T2. `test_fix_diagonal_paths_skips_orthogonal_x`
- [ ] T3. `test_fix_diagonal_paths_skips_zero_y`
- [ ] T4. `test_fix_arrow_labels_to_syntax`

## Phase 6 — Verification
- [ ] V1. `uv run ruff check src/` → 0 violations
- [ ] V2. `uv run pytest tests/ --cov-fail-under=85` → all pass
- [ ] V3. Verify `TikzLayout` in reviewer profile list
- [ ] V4. git commit + push
