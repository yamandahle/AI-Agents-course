# PRD: Content Quality — References, Figure/Table Alignment, Table Layout

## Problem Statement

Three recurring content quality violations in each generated article:

### Bug 1 — Placeholder References
LLM invents domain-name citation keys (`aha.org`, `digiqt.com`, `snowflake.com`).
Bibliography repair creates `@misc` stubs with:
- Author = domain-derived string ("Aha", "Digiqt")
- Title = same
- URL = root domain only (`https://aha.org`) — not a specific article URL
Result: References section contains marketing homepage links with no academic metadata.

### Bug 2 — Figure/Table ↔ Prose Mismatch
Figure axis labels use generic placeholders (`A, B, C, D, E`) but prose says
"mammography", "retinal scans", "pathology slides". Table column values don't match
the terms discussed in the surrounding text. Reader cannot cross-reference.

### Bug 3 — Hardcoded Table Column Sizes
LLM generates `{|l|c|r|}`, `{llll}`, `{p{0.3\textwidth}}` column specs.
These overflow `\textwidth` (tabcolsep not subtracted), cause text truncation,
and ignore word-wrap. `\RaggedRight` (which requires `ragged2e`) is also missing.

---

## Root Causes

| Bug | Root cause |
|-----|-----------|
| 1 | Citation key allow-list in prompt includes domain-name keys; bib-repair creates low-quality stubs |
| 2 | No prompt rule requiring axis labels to match prose text |
| 3 | No `\usepackage{ragged2e}`; prompt table rule lacks `>{\RaggedRight\arraybackslash}X` syntax |

---

## Fixes

### Fix A — Draft Prompt (`_draft_prompt.py`)
1. Add `\usepackage{ragged2e}` to preamble template
2. Update table column spec to `>{\RaggedRight\arraybackslash}X` everywhere
3. Add **Verification Constraint** (exact user text) for references
4. Add **Structural Code Alignment** rule for figures/tables
5. Add **LaTeX Layout Constraint** (exact user text) for table columns
6. Restrict citation key allow-list to ONLY academic/institutional entries with deep-link URLs
   — remove all domain-name keys (aha.org, digiqt.com, etc.)

### Fix B — Sanitizer (`latex_sanitizer.py`)
1. `_fix_missing_ragged2e()` — inject `\usepackage{ragged2e}` if absent
2. `_fix_table_alignment()` — detect `\begin{tabular}` (not tabularx) → convert to tabularx;
   detect bad column specs in tabularx → replace with X columns
3. `validate()` — add check for root-domain-only URLs in references.bib

### Fix C — References Seed (`results/references.bib`)
1. Remove all auto-generated stubs (>= 21 domain-only entries)
2. Remove all `@misc` entries whose URL is a bare root domain (no path)
3. Keep: 11 `@article`, 2 `@book`, ~15 curated `@misc` with real deep-link paths
4. Final curated set becomes the new seed for all future pipeline runs

### Fix D — Bibliography Repair (`latex_compiler.py`)
1. Mark auto-created stubs explicitly with `note = {UNVERIFIED STUB}` 
2. Log WARNING for every stub created (already done, but strengthen)
3. Add `_is_placeholder_url(url)` check — if URL is root domain with no path, flag as low-quality

---

## Todo List

- [x] Write PRD
- [x] A1: Add `\usepackage{ragged2e}` to preamble in `_draft_prompt.py`
- [x] A2: Update table template to use `>{\RaggedRight\arraybackslash}X` (all 4 X cols, no p{3cm})
- [x] A3: Add Verification Constraint (citations) to hard rules
- [x] A4: Add Structural Code Alignment rule
- [x] A5: Add LaTeX Layout Constraint rule
- [x] A6: Restrict citation key allow-list to curated 30-key academic/institutional set
- [x] B1: Add `_fix_missing_ragged2e()` to sanitizer
- [x] B2: Add `_fix_table_alignment()` to sanitizer (tabular→tabularx, bad specs→X cols)
- [x] B3: Add validate() check for root-domain-only URLs in references.bib
- [x] C1: Write clean curated `results/references.bib` (11 @article, 3 @book, 16 @misc)
- [x] D1: Update `_repair_missing_citations()` — stubs get `note={UNVERIFIED STUB}`, root-domain URLs logged as WARNING

## Success Criteria

- References list: every entry has Author, Title, Publisher, Year, deep-link URL (not root domain)
- Figures: axis labels match the exact terms discussed in surrounding prose
- Tables: all use `tabularx{\textwidth}` with `>{\RaggedRight\arraybackslash}X` columns
- `sanitizer.validate()` reports 0 issues after pipeline run
