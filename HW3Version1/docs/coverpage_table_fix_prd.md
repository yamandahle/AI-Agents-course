# PRD — Cover Page Redesign + Table Auto-Width Fix
**Project**: HW3Version1 — AI Article Writer  
**Date**: 2026-06-13  
**Authors**: Nagham Manasra & Yaman Dahle  
**Status**: In Progress

---

## Problem Statement

Two bugs remain in the current PDF output:

| # | Element | Defect | Root Cause |
|---|---|---|---|
| 1 | **Cover page — Hebrew mirroring** | Hebrew labels (מאת, קורס, מרצה) followed by Latin text create mirror-image lines where the colon and Latin content float to the wrong side | Mixed-direction paragraphs with no explicit base direction: BiDi algorithm assigns RTL to the whole line because the first strong character is Hebrew, so Latin text shifts left |
| 2 | **Cover page — missing academic structure** | No institution, no logo, wrong authors (Mansour vs Manasra + Dahle), wrong course name, English/Hebrew title not stacked clearly | Prompt template was a placeholder; now have real course details and university logo PNG |
| 3 | **Table 1 — overflow** | Even with `p{0.15\textwidth}` etc., the table overflows because `\tabcolsep` × 8 columns × 2 sides (~48 pt) is not subtracted from the total | `p{fraction}` does not account for inter-column padding; total column widths + padding > \textwidth |

---

## Root Cause Analysis

### Cover Page Hebrew Mirroring
Lines like `{\large מאת: Nagham Mansour\par}` mix RTL Hebrew ("מאת") with LTR Latin in a single unguarded paragraph. LaTeX/luabidi determines paragraph base direction from the first strong character (Hebrew → RTL). The result: "Nagham Mansour" renders on the left, "מאת:" on the right — visually mirrored.

**Fix**: Eliminate all mixed-direction metadata lines. Write the entire metadata block in pure English (no Hebrew label words). Hebrew content on the cover is limited to the Hebrew title/subtitle, which is explicitly wrapped in `\begin{hebrew}...\end{hebrew}`.

### Cover Page — Academic Standard
Required structure per user spec:
1. **University logo** (top center) — `assets/images/uniHaifasymbol.png` (500×500 RGBA PNG)
2. **Institution** — University of Haifa, Department of Information Systems
3. **English title** (center, Huge bold) — primary
4. **Hebrew subtitle** (center, below title) — explicitly direction-wrapped
5. **Metadata block** (lower center, all English):
   - Authors: Nagham Manasra & Yaman Dahle
   - Course: 203.3763 — Orchestration of AI Agents
   - Instructor: Dr. Yoram Segal
6. **Date** (bottom) — June 2026

### Table Auto-Width
`tabular` with `p{fraction\textwidth}` does not account for `\tabcolsep` (default 6pt, applied left+right of every column → 4 columns × 2 × 6pt = 48pt total). Even 0.90\textwidth overflows.

**Fix**: Use `tabularx` package with `X` columns. `tabularx` takes a target width (here `\textwidth`) as its first argument and stretches `X` columns to fill it exactly — it internally subtracts all `\tabcolsep` spacing before distributing the remainder. Zero overflow, zero math required.

---

## Solution

### Fix A — Cover Page
Replace the entire `\begin{titlepage}...\end{titlepage}` block with:
- `\includegraphics[width=5cm]{../assets/images/uniHaifasymbol.png}` at the top (path relative to `results/` cwd)
- Institution text in English
- English title (`\Huge\bfseries`)
- Hebrew subtitle in `{\hebrewfont\large\begin{hebrew}...\end{hebrew}}`
- Pure-English metadata block (no Hebrew label words)
- `\hrule` separator above date
- Date at bottom with `\vfill`

### Fix B — Table
1. Add `\usepackage{tabularx}` to preamble
2. Replace `\begin{tabular}{p{0.15\textwidth}...}` with:
   ```latex
   \begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{3cm}
                                 >{\raggedright\arraybackslash}X
                                 >{\raggedright\arraybackslash}X
                                 >{\raggedright\arraybackslash}X}
   ```
   First column fixed (3cm for short type names), remaining 3 columns are `X` (auto-fill equally).

### Fix C — `_draft_prompt.py` updates
- Add `\usepackage{tabularx}` to preamble template
- Update cover page template to the new academic structure
- Add PNG logo instruction
- Update HARD RULES: mandate `tabularx{\textwidth}` for all tables, ban `p{fraction\textwidth}` pattern

---

## Success Criteria

1. Cover page shows University of Haifa logo at top
2. Cover page shows both English title and Hebrew subtitle with no mirroring/reversed text
3. Authors show "Nagham Manasra & Yaman Dahle"
4. Course shows "203.3763 — Orchestration of AI Agents"
5. Table 1 fits exactly within the text block — zero `Overfull \hbox` warnings for the table
6. Zero LaTeX errors in compilation log

---

# Plan

## Phase 1 — Preamble
1. Add `\usepackage{tabularx}` to `draft_final.tex` preamble (after `\usepackage{array}`)

## Phase 2 — Cover page
2. Replace titlepage block: logo → institution → English title → Hebrew subtitle → metadata (English only) → vfill → date

## Phase 3 — Table
3. Replace `\begin{tabular}{p{0.15\textwidth}...}` with `tabularx{\textwidth}` + p{3cm}/X/X/X

## Phase 4 — Update `_draft_prompt.py`
4. Add `\usepackage{tabularx}` to preamble section
5. Update cover page template with new academic structure + PNG logo instruction
6. Add `tabularx` to table column rules; remove `p{fraction\textwidth}` from allowed patterns

## Phase 5 — Compile & verify
7. 4-pass compile: lualatex → biber → lualatex × 3
8. Check: zero file-not-found, zero table overflow, zero Hebrew mirroring warnings

## Phase 6 — Finalize
9. Copy results to `result for trial5`
10. Commit

---

# TODO List

- [ ] **TODO-1**: Add `\usepackage{tabularx}` to preamble
- [ ] **TODO-2**: Replace titlepage with academic cover page (logo + EN title + HE subtitle + English metadata)
- [ ] **TODO-3**: Replace table `tabular{p{}}` with `tabularx{\textwidth}`
- [ ] **TODO-4**: Update `_draft_prompt.py` — tabularx + cover page template
- [ ] **TODO-5**: Compile 4 passes — verify zero table overflow, zero cover mirroring
- [ ] **TODO-6**: Copy to `result for trial5`
- [ ] **TODO-7**: Commit
