# PRD: Fix BiDi Root Cause — Main Document Language Direction

## Problem Statement

The entire article renders mirrored (RTL) because the LLM generated:
```latex
\setmainlanguage{hebrew}   % WRONG
\setotherlanguage{english}
```

`polyglossia` + `luabidi` treat Hebrew as the base direction. Every paragraph not explicitly
tagged with `\begin{english}` is rendered RTL. Since only the dedicated BiDi section uses
language tags, the abstract, all section headings, tables, and body paragraphs appear reversed.

## Root Cause Analysis

| Cause | Effect |
|---|---|
| `\setmainlanguage{hebrew}` | base direction = RTL for entire document |
| English body text has no `\begin{english}` tag | English paragraphs rendered RTL → mirrored |
| `englishblock` uses only `\normalfont` | no direction override → RTL when Hebrew is main language |

## Correct Architecture

```
\setmainlanguage{english}    ← LTR base; NO wrapping needed for English
\setotherlanguage{hebrew}    ← Hebrew available as secondary

English text anywhere in body → LTR (automatic, no tags)
Hebrew text                  → MUST be inside hebrewblock or \begin{hebrew}...\end{hebrew}
```

## Proposed Fixes

### Fix A — draft_final.tex (immediate)
1. Line 4: `\setmainlanguage{hebrew}` → `\setmainlanguage{english}`
2. Line 5: `\setotherlanguage{english}` → `\setotherlanguage{hebrew}`
3. Restore `\setlength{\headheight}{14pt}` (dropped in last re-generation)
4. Update `englishblock` env to include `\begin{LTR}...\end{LTR}` (defense-in-depth against future wrong main language)

### Fix B — latex_sanitizer.py
Add `_fix_wrong_main_language()`:
- Detects `\setmainlanguage{hebrew}` → replaces with `\setmainlanguage{english}`
- Ensures `\setotherlanguage{hebrew}` is present
- Removes `\setotherlanguage{english}` (it conflicts when english is main)

Update `_ENGLISHBLOCK_DEF` to include `\begin{LTR}...\end{LTR}`.

### Fix C — _draft_prompt.py
- Hard-code `\setmainlanguage{english}` with bold warning: NEVER change to hebrew
- Update `englishblock` definition to include `\begin{LTR}`
- Add hard rule: "Do NOT change `\setmainlanguage`. It is always `english`."

## Todo List

- [x] Write PRD
- [ ] Fix draft_final.tex: main language lines 4-5
- [ ] Fix draft_final.tex: add headheight
- [ ] Fix draft_final.tex: update englishblock with \begin{LTR}
- [ ] Fix latex_sanitizer.py: add _fix_wrong_main_language
- [ ] Fix latex_sanitizer.py: update _ENGLISHBLOCK_DEF with LTR wrapper
- [ ] Fix _draft_prompt.py: hard warning + englishblock with LTR
- [ ] Recompile and verify 0 BiDi mirroring artifacts
- [ ] Validate with sanitizer.validate()

## Success Criteria

- All English text renders LTR (left to right)
- All Hebrew text renders RTL (right to left) inside blue tcolorboxes
- No reversed characters or mirrored layout in any section
- `sanitizer.validate()` returns empty issues list
- PDF: 20+ pages, 0 errors
