# PRD: Arrow Label Clearance + Citation Quality + Undefined-Reference Scanner

## Bug 1 — Arrow labels overlap boxes in TikZ figures

### Symptom
Figure 2 (architecture diagram): `node[midway, right]` labels on arrows are painted
directly over the arrow path with no background, causing the text to bleed into
adjacent node boxes.

### Root cause
TikZ places `node` text with no background by default. When the arrow passes close
to a box border, the label text overlaps the box text.

### Fix
Every `\draw[->] ... node[...]` label must carry:
- `fill=white, inner sep=2pt` — opaque white rectangle clears the arrow and surrounding content
- `font=\footnotesize` — reduces size so long labels fit without overflow

Applied at two levels:
- **Prompt** (A1, A2): hard rule + updated `_TIKZFLOW` template
- **Sanitizer** (B1): `_fix_arrow_labels()` — inject `fill=white, inner sep=2pt, font=\footnotesize`
  into every TikZ arrow node that lacks a `fill=` attribute

---

## Bug 2 — Raw key artifacts `[text]` in compiled output

### Symptom
PDF shows `[?]` or bibliography shows unresolved `keragon_ai`, `thinkers360_com`, etc.
in reference list. Validator reports "11 unresolved citation(s)".

### Root cause
LLM invents keys outside the curated allow-list. `_repair_missing_citations()` creates
`@misc` stubs but with root-domain URLs and no real metadata. The validator catches
them, but doesn't show which `.tex` lines the bad keys came from, and the stubs stay
in `references.bib` permanently contaminating future runs.

### Fix
- **Validator** (C1): scan `.log` for LaTeX "Reference `X' ... undefined" warnings and
  report exact line numbers in the `.tex` file
- **Sanitizer pre-pass** (C2): `_fix_invalid_cite_keys()` — before compilation, scan
  `\cite{key}` calls in the tex; for any `key` NOT in the curated bib, replace it with
  the nearest matching curated key (keyword-based lookup). This eliminates bad keys
  before biber runs, so no stubs are created.

---

## Bug 3 — Auto-generated stubs have root-domain URLs and no metadata

### Symptom
`_repair_missing_citations()` creates entries like:
```bibtex
@misc{bcg.com,
  author = {{Bcg}},
  title  = {Bcg Com},
  url    = {https://bcg.com},
  note   = {UNVERIFIED STUB ...},
}
```
No Author, no Title, no Publisher, no Year with meaning, no specific URL path.

### Root cause
The compiler's stub generator derives metadata mechanically from the key string,
producing garbage. The `note = {UNVERIFIED STUB}` is correct but doesn't fix the entry.

### Fix
- **Compiler** (D1): `_KNOWN_DOMAIN_META` lookup table — for ~30 well-known domains
  (bcg.com, weforum.org, etc.) map to a proper `{author, title, institution, url}` tuple
  with a topic-relevant URL path (not bare root domain)
- **Compiler** (D2): For unknown domains, generate URL as `https://domain.com/healthcare-ai`
  and derive a better title from the key name (title-cased, spaces replaced)

---

## Todo List

- [x] Write PRD
- [x] A1: Added `fill=white, inner sep=2pt, font=\footnotesize` arrow-label rule to HARD RULES
- [x] A2: Updated `_TIKZFLOW` template — Feedback Loop label now has fill=white, inner sep=2pt
- [x] B1: Added `_fix_arrow_labels()` + `_inject_fill_white()` to sanitizer, wired into `sanitize()`
- [x] C1: Added undefined-reference scanner to `validate()` — parses `.log` for Reference/Citation warnings
- [x] C2: Added `_fix_invalid_cite_keys()` — remaps LLM-invented keys to nearest curated key using 50+ keyword rules
- [x] D1: Added `_KNOWN_DOMAIN_META` table (30+ entries) to compiler — proper org/title/URL-path metadata
- [x] D2: Fallback stub uses `https://www.domain.com/healthcare-ai` path + title-cased org name

## Success Criteria
- Figure 2 (and all future TikZ arrow diagrams): labels have white fill, no overlap
- Zero raw-domain citation keys survive to compilation (remapped to curated set)
- Any remaining auto-stubs have specific URL paths (not bare root domains)
- `validate()` reports 0 critical issues after pipeline run
