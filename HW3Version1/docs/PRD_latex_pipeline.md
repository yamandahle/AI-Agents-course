# PRD — LaTeX Pipeline
**Per-Mechanism Product Requirements**

| Field | Value |
|---|---|
| Version | 1.00 |
| Mechanism | LaTeX Compilation Pipeline |
| Files | `src/article_writer/latex/*.py` |

## Scope
The LaTeX pipeline takes a `.tex` file produced by the WriterAgent and compiles it to a PDF using LuaLaTeX. It validates page count and handles BiDi (Hebrew-English) text.

## Required LaTeX Packages
| Package | Purpose |
|---|---|
| `polyglossia` | Hebrew + English BiDi (LuaLaTeX native) |
| `fontspec` | Unicode font selection |
| `geometry` | Page margins (a4paper, 2.5cm) |
| `hyperref` | Linked TOC and citations |
| `biblatex` + biber | Bibliography management |
| `tikz` | Diagrams and graphics |
| `graphicx` | Image inclusion |
| `booktabs` | Professional tables |
| `amsmath` | Mathematical formulas |
| `fancyhdr` | Headers and footers |
| `listings` | Code listings |

## Compilation Sequence
```
Pass 1: lualatex -interaction=nonstopmode article_final.tex  → generates .aux
Pass 2: biber article_final                                   → processes .bib
Pass 3: lualatex -interaction=nonstopmode article_final.tex  → resolves citations
Pass 4: lualatex -interaction=nonstopmode article_final.tex  → resolves all cross-refs
```

## BiDi Handler
- Detects Hebrew characters (Unicode range U+0590–U+05FF)
- Wraps Hebrew blocks in `\begin{hebrew}...\end{hebrew}`
- Wraps English blocks in `\begin{english}...\end{english}`
- Inline LTR in RTL context: `\textLR{text}`

## Validation
- LaTeX source must contain: `\begin{document}`, `\end{document}`, `\maketitle`, `\tableofcontents`
- Compiled PDF must have ≥ 15 pages (extracted from .log file)
- Zero LaTeX errors in .log file (no "Error" lines)
- Zero undefined references (\ref warnings)

## Acceptance Criteria
- AC-L1: LaTeXCompiler runs exactly N passes (configurable via `latex.compile_passes`)
- AC-L2: biber is called between pass 1 and pass 2
- AC-L3: CompilationError raised if lualatex exit code ≠ 0
- AC-L4: CompilationError raised if PDF < 15 pages
- AC-L5: BiDiHandler correctly wraps Hebrew text in polyglossia `{hebrew}` environment
- AC-L6: All subprocess calls use list args (no `shell=True`)
