# PRD — Graphics, Charts & Table Rendering Fix
**Project**: HW3Version1 — AI Article Writer  
**Date**: 2026-06-12  
**Author**: Nagham Mansour  
**Status**: In Progress

---

## Problem Statement

Four distinct rendering defects in the current `draft_final.tex` produce broken or missing visuals in the PDF:

| # | Element | Defect | Root Cause |
|---|---|---|---|
| 1 | **Figure 1** — Diagnostic Accuracy | Box showing raw filename string `diagnostic_accuracy_chart.pdf` | `\includegraphics` references a non-existent file — no actual chart was generated |
| 2 | **Figure 2** — Architectural Diagram | Nodes stacked vertically, arrows missing, no visual flow | Missing `\usetikzlibrary{positioning}` + wrong `below of + xshift` placement + feedback arrow cuts through all nodes |
| 3 | **Table 1** — AI Platforms | No vertical/horizontal grid lines; text truncated mid-word | Column spec `{llll}` has no width → columns overflow; `booktabs` rules present but no vertical lines by design |
| 4 | **"Table 2" stray heading** | A phantom "Table 2:" heading appears with raw citations, breaking visual hierarchy | `\caption*{...}` used without `\usepackage{caption}` — produces an unnumbered float caption that LaTeX renders as a second table caption |

---

## Root Cause Analysis

### Figure 1
The LLM wrote `\includegraphics{diagnostic_accuracy_chart.pdf}` referencing a PDF file that was never generated. No image asset exists in the `results/` directory. LaTeX renders the filename as a text box placeholder when the file is not found.

**Fix**: Replace with a self-contained `pgfplots` `ybar` chart using real literature-backed accuracy values for 5 medical imaging tasks (AI Agent vs. Human Expert). No external files needed.

### Figure 2
The tikzpicture uses `below of=input, xshift=-2cm` syntax which requires the `positioning` library (`\usetikzlibrary{positioning}`). Without it, node placement defaults to stacking. Additionally:
- The feedback arrow `(output) -- (input)` passes through all intermediate nodes (no path routing)
- Arrow style `>=latex'` is deprecated; should use `>=Stealth` from `arrows.meta`

**Fix**: Add `\usetikzlibrary{shapes,arrows.meta,positioning}` to preamble; rewrite node placement with `below left=`, `below right=` from the `positioning` library; route the feedback arrow to the right side with `(out.east)--++(1.5,0)|-(input.east)`.

### Table 1 — Column overflow & text truncation
`{llll}` uses unbounded left-aligned columns. Long strings like "Clinical decision support, data analysis" overflow into adjacent columns. The `booktabs` package intentionally omits vertical rules (correct academic style), but column wrapping requires `p{width}` specifiers.

**Fix**: Replace `{llll}` with `{p{2.8cm}p{2.5cm}p{3.8cm}p{3.5cm}}` so each column wraps at a defined width. Add `\usepackage{array}` for the `>{\raggedright\arraybackslash}` column prefix. Add `\addlinespace` between rows for readability.

### "Table 2" stray heading
`\caption*{...}` is not a standard LaTeX command — it is provided by `\usepackage{caption}`. Without it, the `*` argument is mishandled, producing a second numbered caption "Table 2: ...". The footnote-style note is redundant anyway since the main caption covers the same content.

**Fix**: Remove `\caption*{...}` entirely. Add `\usepackage{caption}` to the preamble as a safety measure for future LLM-generated content.

---

## Solution Summary

1. **Figure 1**: Replace `\includegraphics{...}` with `pgfplots` `ybar` chart (5 tasks × 2 bars each, data values from referenced literature)
2. **Figure 2**: Fix tikz libraries + node placement + feedback arrow routing
3. **Table 1**: Fix column spec to `p{width}` variants; add `\usepackage{array}` and `\usepackage{caption}`; add `\addlinespace` between rows; remove `\caption*`
4. **Prompt guard**: Update `_draft_prompt.py` to forbid `\includegraphics` with external files, specify pgfplots for charts, and define proper table column spec patterns

---

## Success Criteria

1. Figure 1 renders as a real bar chart with labelled axes, two coloured bar series, and a legend
2. Figure 2 renders as a proper flow diagram with boxes, connecting arrows, and a visible adaptive-loop feedback arrow
3. Table 1 shows all text fully wrapped, no truncation, with `\toprule`/`\midrule`/`\bottomrule` visible
4. No "Table 2" phantom heading anywhere in the PDF
5. Zero `LaTeX Warning: File 'diagnostic_accuracy_chart.pdf' not found` lines in the log

---

# Plan

## Phase 1 — Fix preamble
1. Add `\usepackage{pgfplots}`, `\pgfplotsset{compat=1.18}`, `\usepackage{array}`, `\usepackage{caption}` to `draft_final.tex` preamble
2. Add `\usetikzlibrary{shapes,arrows.meta,positioning}` (tikz is already loaded)

## Phase 2 — Fix Figure 1
3. Replace `\includegraphics{diagnostic_accuracy_chart.pdf}` with a `pgfplots` `ybar` chart

## Phase 3 — Fix Figure 2
4. Rewrite the tikzpicture with correct `positioning`-library placement and routed feedback arrow

## Phase 4 — Fix Table 1 + remove phantom Table 2
5. Replace `{llll}` column spec with `p{width}` variants
6. Add `\addlinespace` between rows
7. Remove `\caption*{...}` after `\end{tabular}`

## Phase 5 — Update `_draft_prompt.py`
8. Add pgfplots to the preamble template
9. Add HARD RULE: no `\includegraphics` referencing non-existent files; use pgfplots for charts
10. Add correct table column spec pattern to the prompt

## Phase 6 — Compile & verify
11. Recompile 4 passes; verify zero file-not-found warnings, all visuals render

## Phase 7 — Finalize
12. Copy results to `result for trial4`
13. Commit

---

# TODO List

- [x] Diagnose Figure 1 — `\includegraphics` references missing file
- [x] Diagnose Figure 2 — missing tikz `positioning` library + bad arrow routing
- [x] Diagnose Table 1 — `{llll}` overflow + `\caption*` phantom Table 2
- [x] Validate pgfplots ybar chart compiles cleanly
- [x] Validate fixed tikz architecture diagram compiles cleanly
- [x] Validate fixed `p{width}` table compiles cleanly
- [ ] **TODO-1**: Add `pgfplots`, `array`, `caption` packages + tikz libraries to preamble
- [ ] **TODO-2**: Replace Figure 1 `\includegraphics` with pgfplots bar chart
- [ ] **TODO-3**: Rewrite Figure 2 tikzpicture with positioning library + routed arrows
- [ ] **TODO-4**: Fix Table 1 column spec; add `\addlinespace`; remove `\caption*`
- [ ] **TODO-5**: Recompile — verify all 4 fixes; check log for zero file-not-found warnings
- [ ] **TODO-6**: Update `_draft_prompt.py` — pgfplots template + no-external-files rule
- [ ] **TODO-7**: Copy results to `result for trial4`
- [ ] **TODO-8**: Commit
