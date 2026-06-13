# PRD — Hebrew BiDi Rendering Fix
**Project**: HW3Version1 — AI Article Writer  
**Date**: 2026-06-12  
**Author**: Nagham Mansour  
**Status**: In Progress

---

## Problem Statement

Hebrew text in the generated LaTeX article renders as **blank/invisible characters** in the output PDF. Every Hebrew letter is reported as "Missing character" by LuaLaTeX's HarfBuzz shaper. Additionally, the text direction (right-to-left) is not applied, so any character that does happen to render appears in the wrong order. The reviewer flagged this across all three review iterations; the editor never fixed it because the root causes are in the LaTeX preamble, not in the article text.

---

## Root Cause Analysis

| # | Root Cause | Evidence |
|---|---|---|
| 1 | **Wrong font**: `DejaVu Serif` has no Hebrew OpenType glyphs | `lualatex` log: `Missing character: There is no ר (U+05E8) in font "DejaVu Serif:script=hebr"` — every single Hebrew character is missing |
| 2 | **Missing `luabidi` package**: Not in preamble | Without `\usepackage{luabidi}`, polyglossia cannot apply RTL text direction in LuaLaTeX. Hebrew text flows left-to-right even if the font were correct. |
| 3 | **Editor ignores BiDi reviewer comments** | All three reviews flagged BiDi issues (v1: "Hebrew not followed by English", v2: "English wrapped in `\begin{hebrew}`", v3: "BiDi only in Section 7"). Editor prompt did not prioritise Structure comments at the same weight as Coverage comments, so they were applied last and sometimes dropped. |

---

## Solution

### Fix 1 — Hebrew Font: Replace `DejaVu Serif` with `David CLM`
`David CLM` is part of the **Culmus** open-source Hebrew font project (now installed at `~/.local/share/fonts/`). It has complete Hebrew Unicode coverage and correct OpenType shaping tables for HarfBuzz/LuaLaTeX. Zero missing character warnings in validation test.

### Fix 2 — Add `\usepackage{luabidi}` to preamble
The `luabidi` package (already installed at `/home/nagham1023/texmf/tex/lualatex/luabidi/luabidi.sty`) enables bidirectional text layout in LuaLaTeX. Without it, `\begin{hebrew}...\end{hebrew}` switches the font but not the paragraph direction.

### Fix 3 — Elevate BiDi to Coverage-level priority in reviewer
Add an explicit BiDi check to the reviewer system prompt with `Coverage`-level priority. A missing or broken BiDi section is as critical as a page-count shortage.

### Fix 4 — Editor must treat Structure/BiDi as non-optional
Update the editor system prompt to list BiDi fixes as Priority 1 (same level as Coverage), ensuring Hebrew environments and font usage are corrected before any other change.

### Fix 5 — Draft prompt: BiDi section template
The draft prompt `_draft_prompt.py` must include an explicit code snippet showing the correct BiDi pattern:
```latex
\begin{hebrew}
פסקה עברית...
\end{hebrew}
\begin{english}
English paragraph (same content)...
\end{english}
```
…so the LLM never wraps English text in `\begin{hebrew}` again.

---

## Success Criteria

1. Zero `Missing character` warnings in the lualatex log for the Hebrew section.
2. Hebrew text visible and flowing right-to-left in the rendered PDF.
3. At least one full section (≥2 subsections) with alternating `\begin{hebrew}` / `\begin{english}` blocks per subsection.
4. Reviewer score ≥ 7.0 on the first post-fix iteration (BiDi no longer the top issue).
5. No regression: English sections still render correctly.

---

## Out of Scope

- Installing David Libre (requires sudo; David CLM is a drop-in replacement).
- Changing the base font for English text.
- Altering the research or guideline pipeline.

---

# Plan

## Phase 1 — Font & Package Fix (preamble level)
1. Update `_draft_prompt.py`: change `hebrewfont` to `David CLM`, add `\usepackage{luabidi}`.
2. Patch the **existing** `draft_final.tex` with the same two changes.
3. Recompile `draft_final.tex` — verify zero missing-character warnings and RTL rendering.

## Phase 2 — Agent Prompt Fix (reviewer + editor)
4. Update `reviewer.py` `_REVIEWER_SYSTEM`: add BiDi as an explicit Coverage-level check.
5. Update `editor.py` `_EDITOR_SYSTEM`: elevate BiDi/Hebrew fixes to Priority 1.

## Phase 3 — Re-run pipeline
6. Run `--mode write` to generate a fresh draft with the corrected prompt.
7. Recompile the new draft; verify Hebrew renders correctly.
8. Commit all changes.

---

# TODO List

- [x] Diagnose root causes (font + luabidi + editor priority)
- [x] Install Culmus Hebrew fonts (`David CLM`) via tlmgr
- [x] Validate `David CLM` works with LuaLaTeX (zero missing-char warnings)
- [ ] **TODO-1**: Fix `_draft_prompt.py` — swap font + add luabidi
- [ ] **TODO-2**: Patch existing `draft_final.tex` — swap font + add luabidi
- [ ] **TODO-3**: Recompile `draft_final.tex` — verify Hebrew visible in PDF
- [ ] **TODO-4**: Fix `reviewer.py` — BiDi as explicit Coverage check
- [ ] **TODO-5**: Fix `editor.py` — BiDi at Priority 1
- [ ] **TODO-6**: Run `--mode write` — fresh draft with corrected prompt
- [ ] **TODO-7**: Recompile new draft — confirm end-to-end Hebrew renders
- [ ] **TODO-8**: Copy results to `result for trial2`
- [ ] **TODO-9**: Commit all changes
