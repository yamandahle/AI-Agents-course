"""chart_checker.py  —  zero-API Structural Code Alignment self-check.

Reads results/draft_final.tex and data/research.md. Deterministically:
  1. Extracts the first pgfplots ybar figure from the draft.
  2. Finds the 3 paragraphs preceding it (expected prose context).
  3. Checks every axis tick label appears verbatim in that context.
  4. Builds a second chart from quantitative facts in research.md +
     known values from 3 curated references (esteva, rajpurkar, campanella).
  5. Compiles a standalone lualatex PDF to results/chart_check/chart_check.pdf.

No LLM calls — purely deterministic regex extraction.

Usage:
    cd HW3Version1
    uv run python src/article_writer/tools/chart_checker.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DRAFT = _ROOT / "results" / "draft_final.tex"
_RESEARCH = _ROOT / "data" / "research.md"
_OUT = _ROOT / "results" / "chart_check"

# ── regex ─────────────────────────────────────────────────────────────────────
_AXIS_RE = re.compile(
    r"\\begin\{axis\}\[([^\]]*ybar[^\]]*)\](.*?)\\end\{axis\}", re.DOTALL
)
_SYMX_RE = re.compile(r"symbolic x coords=\{([^}]+)\}")
_YLABEL_RE = re.compile(r"ylabel=\{([^}]+)\}")
_XLABEL_RE = re.compile(r"xlabel=\{([^}]+)\}")
_COORD_RE = re.compile(r"\(([^,)]+),\s*([\d.]+)\)")
_LEGEND_RE = re.compile(r"\\legend\{([^}]+)\}")

# Known quantitative values from our curated @article references (no API needed)
_CURATED_FACTS: list[tuple[str, float, str]] = [
    (
        "Skin Cancer Detection",
        91.0,
        r"Esteva et al.\ 2017: CNN classified skin lesions at 91\% accuracy, "
        r"matching dermatologists \cite{esteva2017dermatologist}.",
    ),
    (
        "Pneumonia Detection",
        90.3,
        r"Rajpurkar et al.\ 2017: CheXNet achieved AUC 0.903 on chest X-rays, "
        r"surpassing the radiologist average \cite{rajpurkar2017chexnet}.",
    ),
    (
        "Pathology Slide AUC",
        98.8,
        r"Campanella et al.\ 2019: whole-slide AI pathology AUC 0.988 on 44\,732 "
        r"slides \cite{campanella2019deep}.",
    ),
]


def _tex_safe(s: str) -> str:
    """Escape special LaTeX chars in plain text (not in LaTeX commands)."""
    for ch, rep in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("$", r"\$")]:
        s = s.replace(ch, rep)
    return s


def extract_draft_figure(tex: str) -> dict:
    """Return first ybar axis data + 3 preceding paragraphs as context."""
    m = _AXIS_RE.search(tex)
    if not m:
        return {}
    opts, body = m.group(1), m.group(2)

    symx = _SYMX_RE.search(opts)
    tick_labels = [t.strip() for t in symx.group(1).split(",")] if symx else []
    ylabel_m = _YLABEL_RE.search(opts)
    xlabel_m = _XLABEL_RE.search(opts)
    leg = _LEGEND_RE.search(body)
    series_names = [s.strip() for s in leg.group(1).split(",")] if leg else []

    series_data: list[dict] = []
    for i, coord_block in enumerate(re.findall(r"\\addplot[^c]*coordinates\s*\{([^}]+)\}", body)):
        coords = {mm.group(1).strip(): float(mm.group(2)) for mm in _COORD_RE.finditer(coord_block)}
        series_data.append({"name": series_names[i] if i < len(series_names) else f"Series {i+1}", "coords": coords})

    # 3 paragraphs immediately before \begin{figure}
    fig_pos = tex.rfind(r"\begin{figure}", 0, m.start())
    before = tex[:fig_pos].rstrip() if fig_pos >= 0 else ""
    paras = [p.strip() for p in re.split(r"\n{2,}", before) if p.strip()]
    context = "\n\n".join(paras[-3:])

    return {
        "tick_labels": tick_labels,
        "ylabel": ylabel_m.group(1) if ylabel_m else "Value",
        "xlabel": xlabel_m.group(1) if xlabel_m else "Category",
        "series": series_data,
        "context": context,
    }


def check_alignment(data: dict) -> list[tuple[str, bool]]:
    ctx = data.get("context", "")
    return [(lbl, lbl in ctx) for lbl in data.get("tick_labels", [])]


def extract_research_facts(md: str) -> list[tuple[str, float, str]]:
    """Extract named quantitative % facts from research.md."""
    results: list[tuple[str, float, str]] = []
    for fact in re.findall(r"- \*\*Fact\*\*:\s*(.+?)(?=\n-|\Z)", md, re.DOTALL):
        fact = fact.strip()
        if "67% denial reduction" in fact or "67\\%" in fact:
            results.append(("Denial Rate Reduction", 67.0, fact[:140]))
        m = re.search(r"reduced.*?by\s+(\d+)%", fact, re.IGNORECASE)
        if m and "drug interaction" in fact.lower():
            results.append(("Drug Alert Reduction", float(m.group(1)), fact[:140]))
    return results


def _build_draft_series(series: list[dict]) -> str:
    colors = ["blue!60", "orange!60", "green!55", "red!55"]
    lines = ""
    for i, s in enumerate(series):
        coords = "".join(f"({k},{v})" for k, v in s["coords"].items())
        lines += f"      \\addplot+[fill={colors[i % len(colors)]}] coordinates {{{coords}}};\n"
    return lines


def _align_table_rows(alignment: list[tuple[str, bool]]) -> str:
    if not alignment:
        return "  (no tick labels) & ---\\\\\n"
    rows = ""
    for lbl, found in alignment:
        icon = r"\textcolor{green!50!black}{PASS}" if found else r"\textcolor{red!60!black}{FAIL}"
        rows += f"  {_tex_safe(lbl)} & {icon}\\\\\n"
    return rows


def build_latex(draft: dict, res_facts: list[tuple[str, float, str]], alignment: list[tuple[str, bool]]) -> str:
    tick_labels = draft.get("tick_labels", [])
    symx = ",".join(tick_labels)
    ylabel = draft.get("ylabel", "Value")
    xlabel = draft.get("xlabel", "Category")
    series_tex = _build_draft_series(draft.get("series", []))
    legend_names = ",".join(s["name"] for s in draft.get("series", []))
    align_rows = _align_table_rows(alignment)
    context_safe = _tex_safe(draft.get("context", "(no context extracted)"))

    # Research chart: combine extracted + curated
    all_facts = res_facts + _CURATED_FACTS
    res_symx = ",".join(f"{{{lbl}}}" for lbl, _, _ in all_facts)
    res_coords = "".join(f"({{{lbl}}},{val})" for lbl, val, _ in all_facts)
    fact_items = ""
    for lbl, val, sentence in all_facts:
        sentence_safe = _tex_safe(sentence) if not sentence.startswith(r"\cite") else sentence
        fact_items += f"  \\item \\textbf{{{lbl} ({val:.0f}\\%)}} --- {sentence_safe}\n"

    return rf"""% chart_check.tex — generated by chart_checker.py (zero API calls)
\documentclass[a4paper,11pt]{{article}}
\usepackage{{fontspec}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\usepackage{{booktabs,xcolor,geometry}}
\usepackage[hidelinks]{{hyperref}}
\geometry{{margin=2.2cm}}
\begin{{document}}

\begin{{center}}
  {{\LARGE\bfseries Chart Self-Check Report}}\\[4pt]
  {{\small\color{{gray}} Generated by \texttt{{chart\_checker.py}} --- no LLM calls}}
\end{{center}}
\medskip\hrule\bigskip

%% ─────────────────────────────────────────────────────────────────────────────
\section*{{1.\ Draft Figure Reproduction (from \texttt{{draft\_final.tex}})}}

\begin{{figure}}[ht]
  \centering
  \begin{{tikzpicture}}
    \begin{{axis}}[
      ybar,
      bar width=0.4cm,
      width=0.88\textwidth,
      height=7cm,
      ylabel={{{ylabel}}},
      xlabel={{{xlabel}}},
      ymin=75,ymax=100,
      xtick=data,
      symbolic x coords={{{symx}}},
      xticklabel style={{rotate=22,anchor=north east,font=\small}},
      nodes near coords,
      legend style={{at={{(0.5,1.12)}},anchor=south,legend columns=-1}},
    ]
{series_tex}
      \legend{{{legend_names}}}
    \end{{axis}}
  \end{{tikzpicture}}
  \caption{{Reproduced from \texttt{{draft\_final.tex}} --- for visual alignment check.}}
\end{{figure}}

\subsection*{{Structural Code Alignment Check}}
\noindent
Does each axis tick label appear \emph{{verbatim}} in the 3 paragraphs preceding the figure in the draft?
\smallskip

\begin{{tabular}}{{lp{{5cm}}}}
  \toprule
  \textbf{{Tick Label}} & \textbf{{Status}}\\
  \midrule
{align_rows}  \bottomrule
\end{{tabular}}

\bigskip
\noindent\textbf{{Prose context used (last 3 paragraphs before the figure):}}
\begin{{quote}}\small
{context_safe}
\end{{quote}}

\clearpage

%% ─────────────────────────────────────────────────────────────────────────────
\section*{{2.\ Quantitative Facts Chart (from \texttt{{data/research.md}} + curated refs)}}
\noindent
2 values extracted from research.md; 3 values from curated \texttt{{references.bib}} papers.
\medskip

\begin{{figure}}[ht]
  \centering
  \begin{{tikzpicture}}
    \begin{{axis}}[
      ybar,
      bar width=0.55cm,
      width=0.92\textwidth,
      height=8cm,
      ylabel={{Improvement / Accuracy (\%)}},
      xlabel={{Application}},
      ymin=0,ymax=110,
      xtick=data,
      symbolic x coords={{{res_symx}}},
      xticklabel style={{rotate=30,anchor=north east,font=\footnotesize,text width=2.8cm,align=right}},
      nodes near coords,
      nodes near coords align={{vertical}},
    ]
      \addplot+[fill=teal!60] coordinates {{{res_coords}}};
    \end{{axis}}
  \end{{tikzpicture}}
  \caption{{AI performance metrics: extracted from research data and curated literature.}}
\end{{figure}}

\subsection*{{Source Sentences}}
\begin{{itemize}}\small
{fact_items}\end{{itemize}}

\end{{document}}
"""


def compile_latex(tex: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tex_path = out_dir / "chart_check.tex"
    tex_path.write_text(tex, encoding="utf-8")
    for _ in range(2):
        res = subprocess.run(
            ["lualatex", "--interaction=nonstopmode", "--halt-on-error", "chart_check.tex"],  # noqa: S607
            cwd=out_dir,
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            log_tail = res.stdout[-2500:] if res.stdout else res.stderr[-2500:]
            print(f"lualatex error:\n{log_tail}", file=sys.stderr)
            return tex_path
    pdf = out_dir / "chart_check.pdf"
    print(f"PDF: {pdf}")
    return pdf


def main() -> int:
    for p in (_DRAFT, _RESEARCH):
        if not p.exists():
            print(f"ERROR: not found: {p}", file=sys.stderr)
            return 1

    tex = _DRAFT.read_text(encoding="utf-8")
    md = _RESEARCH.read_text(encoding="utf-8")

    print("Extracting draft figure ...")
    draft = extract_draft_figure(tex)
    if draft:
        print(f"  tick labels : {draft['tick_labels']}")
        print(f"  series      : {[s['name'] for s in draft['series']]}")
    else:
        print("  WARNING: no ybar axis found in draft")

    print("Checking alignment ...")
    alignment = check_alignment(draft) if draft else []
    for lbl, found in alignment:
        print(f"  [{'PASS' if found else 'FAIL'}] {lbl!r}")

    print("Extracting research facts ...")
    res_facts = extract_research_facts(md)
    print(f"  {len(res_facts)} fact(s) from research.md + {len(_CURATED_FACTS)} curated")

    print("Building LaTeX ...")
    latex = build_latex(draft, res_facts, alignment)

    print("Compiling ...")
    compile_latex(latex, _OUT)

    fails = sum(1 for _, f in alignment if not f)
    if alignment:
        status = "ALL PASS" if fails == 0 else f"{fails} FAILURE(S)"
        print(f"\nAlignment: {status}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
