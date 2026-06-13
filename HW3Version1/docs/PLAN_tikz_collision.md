# Plan — TikZ Spatial Collision Prevention

## Phase 1 — Writer prompt (W1, W2)
File: `src/article_writer/writing/_draft_prompt.py`

Insert a **TIKZ FLOWCHART RULES** block inside CONTENT REQUIREMENTS §2b (after the pgfplots
example), and strengthen the existing ARROW LABELS hard rule.

Key rules to encode:
- Every `node[midway, ...]` on an arrow path must carry `fill=white, inner sep=2pt`
- Feedback / return paths must use `|-` or `-|` (orthogonal bend) never bare `--`
- Routes that would cross box borders must be shifted with `xshift` / `yshift`
- Explicit example of a clean feedback loop with `to[out=0,in=0, looseness=1.4]`

## Phase 2 — Reviewer prompt (R1)
File: `src/article_writer/writing/reviewer.py` → `_REVIEWER_SYSTEM`

Add `TikzLayout` as priority item 3 (between Structure and Accuracy).
Rejection criteria:
- Any connection label node without `fill=white` or `fill=pagecolor`
- Any `\draw` path using bare `--` for a multi-hop route that could cross a box

Add "TikzLayout" to the allowed `profile` values list.

## Phase 3 — Editor prompt (E1)
File: `src/article_writer/writing/editor.py` → `_EDITOR_SYSTEM`

Insert TikZ collision fix as priority item 2 (immediately after BiDi, before Coverage).
Include the exact repair pattern (orthogonal `|-` routing + `fill=white` on labels).

Update `_format_comments` priority_order list to include `"TikzLayout"`.

## Phase 4 — Sanitizer Fix 12 (S1, S2)
File: `src/article_writer/latex/latex_sanitizer.py`

Add `_fix_diagonal_paths(self, source: str) -> tuple[str, int]`:
- Regex: `-- \+\+\(([^,)]+),([^)]+)\)` — match `-- ++(x,y)` segments
- Skip when x==0 or y==0 (already orthogonal)
- Rewrite as `-- ++(x,0) -- ++(0,y)`

Wire into `sanitize()` as Fix 12 (n12), update total and log line.

## Phase 5 — Tests (T1–T4)
File: `tests/unit/test_latex/test_tikz_collision.py`

- T1: `test_fix_diagonal_paths_converts_diagonal` — basic conversion
- T2: `test_fix_diagonal_paths_skips_orthogonal` — `++(3cm,0)` unchanged
- T3: `test_fix_diagonal_paths_skips_zero_y` — `++(0,-2cm)` unchanged
- T4: `test_fix_arrow_labels_also_fires_on_draw_to` — edge node on `\draw[->] (A) to`

## Phase 6 — Verification (V1–V4)
- V1: `uv run ruff check src/` → 0 violations
- V2: `uv run pytest tests/ --cov-fail-under=85` → all pass
- V3: Confirm `TikzLayout` profile in reviewer prompt
- V4: git commit + push
