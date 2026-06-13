# PRD — TikZ Spatial Collision Prevention

## Problem Statement

TikZ flowcharts and system-architecture diagrams produced by the writer agent suffer from
two recurring layout bugs that degrade PDF quality:

1. **Label bleed** — arrow-path labels (`node[midway]`) have no background, so the arrow
   line visually bleeds through the text characters.
2. **Diagonal crossing** — feedback loops and return paths are drawn as straight diagonal
   lines that physically cross intermediate boxes and other arrow paths.

The sanitizer already patches `fill=white` onto naked `node[midway]` labels (Fix 9), but
the writer still generates diagonal multi-hop paths and the reviewer never flags them.

## Goals

| ID  | Goal |
|-----|------|
| G1  | Writer prompt encodes orthogonal-routing rules so the LLM generates clean paths first time |
| G2  | Reviewer prompt adds a `TikzLayout` violation category so spatial collisions are caught and trigger an editor pass |
| G3  | Editor prompt gives TikZ collision fixes the highest correction priority |
| G4  | Sanitizer adds Fix 12 — convert diagonal `++(x,y)` coordinate waypoints to two-step orthogonal `++(x,0) ++(0,y)` |
| G5  | All changes are covered by unit tests; ruff + pytest ≥85% remain green |

## Non-Goals

- Automatic layout of entire TikZ graphs (requires coordinate solver)
- Converting pgfplots charts (only tikzpicture flowcharts are in scope)
- Removing arrow labels that already have `fill=white`

## Requirements

| ID  | Requirement |
|-----|-------------|
| R1  | `_draft_prompt.py` gains a dedicated **TIKZ FLOWCHART RULES** block with: (a) `fill=white` mandate on every label node, (b) orthogonal routing rule for feedback/return paths using `|-` or `-|` or `to[out=..,in=..]`, (c) `xshift`/`yshift` guidance for routing lines clear of boxes |
| R2  | `_draft_prompt.py` HARD RULES section strengthens the existing ARROW LABELS rule to also forbid straight `--` multi-hop paths |
| R3  | `reviewer.py` `_REVIEWER_SYSTEM` adds `TikzLayout` as the 3rd priority check (between Structure and Accuracy); lists two explicit rejection criteria |
| R4  | `editor.py` `_EDITOR_SYSTEM` adds TikZ collision fixes to its priority list immediately after BiDi |
| R5  | `latex_sanitizer.py` gains `_fix_diagonal_paths()` (Fix 12): detects `-- ++(x,y)` diagonal segments where both x and y are non-zero and rewrites them as `-- ++(x,0) -- ++(0,y)` |
| R6  | `sanitize()` calls `_fix_diagonal_paths` and includes its count in the totals log |
| R7  | New `tests/unit/test_latex/test_tikz_collision.py` covers Fix 12 and existing Fix 9 edge cases |
