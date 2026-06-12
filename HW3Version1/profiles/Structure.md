# Writing Profile — Structure

## Document Skeleton (Required Order)
1. Cover page — `\begin{titlepage}` with: title, author, date, course, lecturer
2. `\newpage` + `\tableofcontents` + `\newpage`
3. Body chapters — numbered `\section{}`, `\subsection{}`, `\subsubsection{}`
4. Bibliography — `\printbibliography` with `heading=bibintoc`

## Chapter Requirements
- Minimum 5 numbered sections
- Each section minimum 2 subsections
- Minimum 1 chapter must be a Hebrew-English BiDi chapter (polyglossia)
- BiDi chapter: use `\begin{hebrew}...\end{hebrew}` and `\begin{english}...\end{english}` blocks

## Mandatory Content Elements (placed in body)
| Element | LaTeX Environment | Placement Rule |
|---|---|---|
| Image | `\begin{figure}[H]` with `\caption{}` | After first mention in text |
| Python Graph | `\includegraphics{}` in `figure` env | In results/analysis chapter |
| Table | `\begin{table}[H]` + `tabular` + booktabs | After first mention in text |
| Formula | `\begin{equation}\label{eq:N}\end{equation}` | Within relevant theory section |

## Headers and Footers
- Use `\pagestyle{fancy}` via fancyhdr
- Header left: `\leftmark` (section name)
- Header right: page number
- Footer center: course name + date
- Cover page: `\thispagestyle{empty}`

## Numbering and References
- Every `\section`, `\subsection`, `\figure`, `\table`, `\equation` must have a `\label{}`
- Every reference to them must use `\ref{}` or `\eqref{}`
- Cross-references must resolve — run lualatex 4 times

## Paragraph Rules
- No blank sections — every section must have at least 2 paragraphs of content
- No orphan headings — a heading must be followed by text, not another heading
- Introduction must state the article's purpose, structure, and relevance
- Conclusion must synthesize at minimum 3 findings from the body
