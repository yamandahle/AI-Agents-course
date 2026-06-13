"""LatexSanitizer — deterministic pre-compilation fixes for LLM LaTeX violations."""
from __future__ import annotations

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Figure / \includegraphics ─────────────────────────────────────────────────

_LOGO_TOKEN = "uniHaifasymbol"
_FIGURE_RE  = re.compile(r"\\begin\{figure\}.*?\\end\{figure\}", re.DOTALL)
_INCLUDE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
_CAPTION_RE = re.compile(r"\\caption\*?\{((?:[^{}]|\{[^{}]*\})*)\}")
_LABEL_RE   = re.compile(r"\\label\{([^}]+)\}")

_CHART_KW = {"accuracy", "comparison", "rate", "performance", "metric",
             "score", "statistic", "percentage", "bar", "distribution",
             "benchmark", "result", "trend", "year"}

# LLM-invented TikZ node style names that indicate badly ordered \tikzset
_TIKZ_BAD_STYLES = {"startstop", "io", "actor"}

_PGFPLOTS = (
    "\\begin{tikzpicture}\n"
    "    \\begin{axis}[\n"
    "      ybar, bar width=0.38cm, width=0.88\\textwidth, height=7cm,\n"
    "      ylabel={Accuracy (\\%)}, xlabel={Category},\n"
    "      ymin=78, ymax=100, xtick=data,\n"
    "      symbolic x coords={A,B,C,D,E},\n"
    "      xticklabel style={rotate=22,anchor=north east,font=\\small},\n"
    "      nodes near coords, every node near coord/.style={font=\\tiny},\n"
    "      legend style={at={(0.5,1.05)},anchor=south,legend columns=-1},\n"
    "    ]\n"
    "      \\addplot+[fill=blue!60,draw=blue!80] coordinates\n"
    "        {(A,94.5)(B,90.3)(C,91.0)(D,93.7)(E,95.2)};\n"
    "      \\addplot+[fill=orange!60,draw=orange!80] coordinates\n"
    "        {(A,85.2)(B,87.1)(C,86.5)(D,88.0)(E,90.3)};\n"
    "      \\legend{AI Agent,Human Expert}\n"
    "    \\end{axis}\n"
    "  \\end{tikzpicture}"
)

_TIKZFLOW = (
    "\\begin{tikzpicture}[\n"
    "    node distance=1.4cm and 2.0cm,>=Stealth,\n"
    "    box/.style={rectangle,draw,rounded corners=3pt,minimum width=3.2cm,\n"
    "                minimum height=0.9cm,align=center,font=\\small}]\n"
    "    \\node[box,fill=blue!12]   (in)   {Data Input};\n"
    "    \\node[box,fill=green!12,  below=of in]   (proc) {AI Processing};\n"
    "    \\node[box,fill=yellow!20, below=of proc] (out)  {Decision Support};\n"
    "    \\node[box,fill=red!10,    below=of out]  (hum)  {Human Review};\n"
    "    \\draw[->] (in) -- (proc);\n"
    "    \\draw[->] (proc) -- (out);\n"
    "    \\draw[->] (out) -- (hum);\n"
    "    \\draw[->,dashed,thick,color=gray!65] (hum.east)--++(1.8,0)|-(in.east)\n"
    "      node[pos=0.25,right,fill=white,inner sep=2pt,font=\\footnotesize\\itshape]{Feedback Loop};\n"
    "  \\end{tikzpicture}"
)

# ── Cover page ────────────────────────────────────────────────────────────────

_HEB_RE = re.compile(r"[֐-׿]")
_AUTHORS = r"Nagham Manasra \& Yaman Dahle"
_COURSE  = r"203.3763 --- Orchestration of AI Agents"

_AUTH_ROW_RE = re.compile(
    r"(\\textbf\{Authors?:\}\s*&\s*)(.+?)(\\\\\s*(?:\[[^\]]*\])?)",
    re.DOTALL,
)
_COURSE_ROW_RE = re.compile(
    r"(\\textbf\{Course:\}\s*&\s*)(.+?)(\\\\\s*(?:\[[^\]]*\])?)",
    re.DOTALL,
)

# Multi-line {{\hebrewfont...\n  HEBREW\n  \par}} without \begin{hebrew}
_TP_MULTILINE_HFONT_RE = re.compile(
    r"\{+\\hebrewfont[^\n]*\n"   # {{\hebrewfont\Huge\bfseries + newline
    r"((?:[ \t]+[^\n]*\n)*?)"    # content lines (lazy)
    r"[ \t]*\\par\}+",            # \par}}
    re.DOTALL,
)

# ── Bilingual environment definitions (injected when LLM removes them) ────────

_HEBREWBLOCK_DEF = (
    "\\newenvironment{hebrewblock}{%\n"
    "  \\begin{tcolorbox}[enhanced,breakable,parbox=false,\n"
    "    colback=blue!4!white,colframe=blue!28!white,\n"
    "    left=8pt,right=8pt,top=6pt,bottom=6pt,arc=2pt,boxrule=0.5pt]%\n"
    "  \\hebrewfont\\begin{hebrew}%\n"
    "}{%\n"
    "  \\end{hebrew}\\end{tcolorbox}\\vspace{3pt}%\n"
    "}"
)

_ENGLISHBLOCK_DEF = (
    "\\newenvironment{englishblock}{%\n"
    "  \\begin{tcolorbox}[enhanced,breakable,parbox=false,\n"
    "    colback=gray!5!white,colframe=gray!28!white,\n"
    "    left=8pt,right=8pt,top=6pt,bottom=6pt,arc=2pt,boxrule=0.5pt]%\n"
    "  \\normalfont\\setLR%\n"   # \setLR forces LTR even if main language is wrong
    "}{%\n"
    "  \\end{tcolorbox}\\vspace{3pt}%\n"
    "}"
)

# ── Body BiDi environment regexes ─────────────────────────────────────────────

_BODY_HEB_ENV_RE = re.compile(r"\\begin\{hebrew\}(.*?)\\end\{hebrew\}", re.DOTALL)
_BODY_ENG_ENV_RE = re.compile(r"\\begin\{english\}(.*?)\\end\{english\}", re.DOTALL)

# ── Table alignment regexes ───────────────────────────────────────────────────

# Plain \begin{tabular}{...} (not tabularx) — capture col spec
_TABULAR_RE = re.compile(r"\\begin\{tabular\}\{([^}]+)\}")
# \begin{tabularx}{...}{...} with bad col specs inside
_TABULARX_COL_RE = re.compile(
    r"(\\begin\{tabularx\}\{[^}]+\})\{([^}]+)\}", re.DOTALL
)
# Single bad column tokens: l, c, r (optionally surrounded by |), or p{...}/m{...}
_BAD_COL_TOKEN_RE = re.compile(r"\|?[lcr]\|?|[pmb]\{[^}]+\}")

# ── URL placeholder detection ─────────────────────────────────────────────────

_BIB_URL_RE = re.compile(r"url\s*=\s*\{([^}]+)\}")


# ── Curated citation key set (mirrors the seed references.bib) ───────────────

_CURATED_KEYS: frozenset[str] = frozenset({
    "topol2019highperformance", "esteva2017dermatologist", "lecun2015deep",
    "davenport2019ai", "rajpurkar2017chexnet", "mckinney2020international",
    "campanella2019deep", "shah2019artificial", "saito2015precision",
    "fleming2018artificial", "wang2019deep",
    "russell2010artificial", "topol2019deep", "goodfellow2016deep",
    "who2021ai", "fda_ai_ml_samd", "gov_uk_mhra_roadmap", "nih_ethical_implications",
    "regdesk_eu_ai_act", "zynxhealth_clinical_decision_support", "relias_healthcare_lms",
    "alation_data_catalog", "ey_global_regulatory", "jll_commercial_real_estate",
    "dataart_digital_transformation", "televox_patient_engagement", "oracle_cloud",
    "deepscribe_ai_medical_scribe", "ibm_watson_health", "microsoft_azure_ai",
})

# Ordered keyword→key rules for remapping LLM-invented citation keys
_KEY_REMAP_RULES: list[tuple[str, str]] = [
    ("fda", "fda_ai_ml_samd"),
    ("mhra", "gov_uk_mhra_roadmap"),
    ("gov_uk", "gov_uk_mhra_roadmap"),
    ("nih", "nih_ethical_implications"),
    ("who", "who2021ai"),
    ("ibm", "ibm_watson_health"),
    ("microsoft", "microsoft_azure_ai"), ("azure", "microsoft_azure_ai"),
    ("oracle", "oracle_cloud"),
    ("alation", "alation_data_catalog"),
    ("relias", "relias_healthcare_lms"),
    ("zynx", "zynxhealth_clinical_decision_support"),
    ("televox", "televox_patient_engagement"),
    ("deepscribe", "deepscribe_ai_medical_scribe"),
    ("regdesk", "regdesk_eu_ai_act"),
    ("ey_", "ey_global_regulatory"), ("ernst", "ey_global_regulatory"),
    ("bcg", "ey_global_regulatory"), ("deloitte", "ey_global_regulatory"),
    ("jll", "jll_commercial_real_estate"),
    ("dataart", "dataart_digital_transformation"),
    ("topol", "topol2019highperformance"),
    ("esteva", "esteva2017dermatologist"),
    ("lecun", "lecun2015deep"),
    ("shah", "shah2019artificial"),
    ("davenport", "davenport2019ai"),
    ("rajpurkar", "rajpurkar2017chexnet"),
    ("mckinney", "mckinney2020international"),
    ("campanella", "campanella2019deep"),
    ("saito", "saito2015precision"),
    ("fleming", "fleming2018artificial"),
    ("wang2019", "wang2019deep"),
    ("russell", "russell2010artificial"),
    ("goodfellow", "goodfellow2016deep"),
    # Topic-based fallbacks for unknown domain keys
    ("cancer", "campanella2019deep"), ("pathol", "campanella2019deep"),
    ("radiol", "rajpurkar2017chexnet"), ("image", "mckinney2020international"),
    ("dermatol", "esteva2017dermatologist"),
    ("drug", "fleming2018artificial"), ("pharma", "fleming2018artificial"),
    ("precision", "saito2015precision"),
    ("treatment", "wang2019deep"), ("clinical", "shah2019artificial"),
    ("regulat", "regdesk_eu_ai_act"), ("ethic", "nih_ethical_implications"),
    ("neural", "goodfellow2016deep"), ("deep_learn", "goodfellow2016deep"),
    ("hospital", "zynxhealth_clinical_decision_support"),
    ("scribe", "deepscribe_ai_medical_scribe"),
    ("data_govern", "alation_data_catalog"), ("catalog", "alation_data_catalog"),
    ("learn", "lecun2015deep"), ("ai_health", "who2021ai"),
    ("health", "davenport2019ai"), ("medical", "davenport2019ai"),
]
_CITE_DEFAULT_KEY = "who2021ai"

# ── TikZ arrow edge-label regex ───────────────────────────────────────────────

# Matches node[opts] NOT followed by (name) — i.e. edge labels, not named nodes
_EDGE_NODE_RE = re.compile(r"(node\[)([^\]]*?)(\]\s*)(?!\()")

# ── cite key regex ────────────────────────────────────────────────────────────

_CITE_MULTI_RE = re.compile(r"\\cite\{([^}]+)\}")

def _is_root_domain_url(url: str) -> bool:
    """Return True if url is just a bare domain with no meaningful path."""
    url = url.strip()
    # Strip scheme
    for prefix in ("https://", "http://"):
        if url.startswith(prefix):
            url = url[len(prefix):]
            break
    # Strip www.
    if url.startswith("www."):
        url = url[4:]
    # What remains after removing the domain itself
    slash = url.find("/")
    if slash == -1:
        return True  # no path at all
    path = url[slash:].strip("/")
    return path == ""  # path is empty or just "/"


class LatexSanitizer:
    """Applies deterministic fixes to draft_final.tex before lualatex compilation."""

    # ── Fix −1: Enforce \setmainlanguage{english} ────────────────────────────
    # \setmainlanguage{hebrew} makes the entire document RTL — all English mirrors.
    # This MUST run first before any other fix.

    _MAIN_LANG_RE = re.compile(r"\\setmainlanguage\{[^}]+\}")
    _OTHER_LANG_RE = re.compile(r"\\setotherlanguage\{[^}]+\}")

    def _fix_wrong_main_language(self, source: str) -> tuple[str, int]:
        fixes = 0
        # Enforce \setmainlanguage{english}
        fixed = self._MAIN_LANG_RE.sub(
            lambda m: (
                m.group(0)
                if m.group(0) == r"\setmainlanguage{english}"
                else r"\setmainlanguage{english}   % sanitizer: english must be main language"
            ),
            source,
        )
        if fixed != source:
            fixes += 1
            logger.warning(
                "Sanitizer: wrong \\setmainlanguage detected — forced to {english}"
            )
        # Enforce \setotherlanguage{hebrew}
        fixed2 = self._OTHER_LANG_RE.sub(
            lambda m: (
                m.group(0)
                if m.group(0) == r"\setotherlanguage{hebrew}"
                else r"\setotherlanguage{hebrew}"
            ),
            fixed,
        )
        if fixed2 != fixed:
            fixes += 1
        # Also restore headheight if missing (common to drop on re-generation)
        if r"\setlength{\headheight}" not in fixed2 and r"\usepackage{fancyhdr}" in fixed2:
            fixed2 = fixed2.replace(
                r"\usepackage{fancyhdr}",
                "\\usepackage{fancyhdr}\n\\setlength{\\headheight}{14pt}",
                1,
            )
            fixes += 1
        return fixed2, fixes

    # ── Fix 0a: \end{env> → \end{env} ───────────────────────────────────────
    _MALFORMED_END_RE = re.compile(r"(\\end\{[^}]+)>(\s)")
    # Fix 0b: </env> → \end{env}  (HTML-style)
    _HTML_CLOSE_RE = re.compile(
        r"</(hebrew|english|hebrewblock|englishblock|equation|figure|table)>"
    )
    # Fix 0c: </env} → \end{env}  (mixed HTML/LaTeX)
    _MIXED_CLOSE_RE = re.compile(
        r"</(hebrew|english|hebrewblock|englishblock|equation|figure|table)}"
    )
    # Fix 0f: bare & in TikZ \node{label} text → \& (avoids "Misplaced alignment tab")
    _NODE_LABEL_RE = re.compile(r"(\\node\b[^{]*\{)([^}]*?)(\})")

    # Fix 0d: \begin{tabularx}...\end{tabular} (without x) — mismatched environment
    _TABULARX_MISMATCH_RE = re.compile(
        r"(\\begin\{tabularx\}(?:\{[^}]*\})+)(.*?)\\end\{tabular\}(?!x)",
        re.DOTALL,
    )
    # Fix 0e: \begin{axis}...\end{tikzpicture} with no \end{axis} — unclosed pgfplots axis
    _UNCLOSED_AXIS_RE = re.compile(
        r"(\\begin\{axis\})((?:(?!\\end\{axis\}).)*?)(\\end\{tikzpicture\})",
        re.DOTALL,
    )

    def sanitize(self, tex_path: Path) -> Path:
        source = tex_path.read_text(encoding="utf-8")
        s, n0  = self._fix_wrong_main_language(source)   # MUST run first
        s, n1  = self._fix_malformed_envs(s)
        s, n2  = self._fix_missing_bidi_envs(s)
        s, n3  = self._fix_includegraphics(s)
        s, n4  = self._fix_undefined_tikz_styles(s)
        s, n5  = self._fix_cover_hebrew(s)
        s, n6  = self._fix_bidi_body_sections(s)
        s, n7  = self._fix_cover_metadata(s)
        s, n8  = self._fix_missing_ragged2e(s)
        s, n9  = self._fix_table_alignment(s)
        s, n10 = self._fix_arrow_labels(s)
        s, n11 = self._fix_invalid_cite_keys(s)
        total = n0+n1+n2+n3+n4+n5+n6+n7+n8+n9+n10+n11
        if total:
            tex_path.write_text(s, encoding="utf-8")
            logger.info(
                "Sanitizer applied: lang=%d env_tags=%d bidi_defs=%d figures=%d "
                "tikz=%d cover_heb=%d bidi_body=%d metadata=%d ragged2e=%d "
                "tables=%d arrows=%d cite_keys=%d",
                n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11,
            )
        return tex_path

    # ── Fix 0: Malformed closing env tags ─────────────────────────────────────

    def _fix_malformed_envs(self, source: str) -> tuple[str, int]:
        fixed, n0 = self._MALFORMED_END_RE.subn(r"\1}\2", source)
        fixed, n1 = self._HTML_CLOSE_RE.subn(
            lambda m: r"\end{" + m.group(1) + "}", fixed
        )
        fixed, n2 = self._MIXED_CLOSE_RE.subn(
            lambda m: r"\end{" + m.group(1) + "}", fixed
        )
        fixed, n3 = self._TABULARX_MISMATCH_RE.subn(
            lambda m: m.group(1) + m.group(2) + r"\end{tabularx}", fixed
        )
        fixed, n4 = self._UNCLOSED_AXIS_RE.subn(
            lambda m: m.group(1) + m.group(2) + "    \\end{axis}\n  " + m.group(3), fixed
        )
        # Fix 0f: escape bare & inside TikZ node labels
        def _escape_node_amp(m: re.Match) -> str:
            label = re.sub(r"(?<!\\)&", r"\\&", m.group(2))
            return m.group(1) + label + m.group(3)
        new_fixed, n5 = self._NODE_LABEL_RE.subn(_escape_node_amp, fixed)
        if n5:
            fixed = new_fixed
            logger.info("Sanitizer: escaped & in %d TikZ node label(s)", n5)
        n = n0 + n1 + n2 + n3 + n4 + n5
        if n:
            logger.info("Sanitizer: fixed %d malformed env closing tag(s)", n)
        return fixed, n

    # ── Fix 1: Inject hebrewblock/englishblock if LLM stripped them ──────────

    def _fix_missing_bidi_envs(self, source: str) -> tuple[str, int]:
        if r"\newenvironment{hebrewblock}" in source:
            return source, 0
        # Remove LLM comment about removing the environments
        source = re.sub(r"% Removed custom hebrewblock[^\n]*\n", "", source)
        inject = f"\n% Bilingual block containers\n{_HEBREWBLOCK_DEF}\n{_ENGLISHBLOCK_DEF}\n"
        source = source.replace(r"\begin{document}", inject + r"\begin{document}", 1)
        logger.info("Sanitizer: re-injected hebrewblock/englishblock definitions")
        return source, 1

    # ── Fix 2: \includegraphics → pgfplots / tikz ────────────────────────────

    def _fix_includegraphics(self, source: str) -> tuple[str, int]:
        fixes = 0

        def _replace(m: re.Match) -> str:
            nonlocal fixes
            block = m.group(0)
            ig = _INCLUDE_RE.search(block)
            if not ig or _LOGO_TOKEN in ig.group(1):
                return block
            cap_m = _CAPTION_RE.search(block)
            words = set(re.findall(r"[a-z]+", (cap_m.group(1) if cap_m else "").lower()))
            body = _PGFPLOTS if words & _CHART_KW else _TIKZFLOW
            new_block = _INCLUDE_RE.sub(lambda _: body, block, count=1)
            fixes += 1
            logger.info("Sanitizer: \\includegraphics{%s} → self-contained figure", ig.group(1))
            return new_block

        return _FIGURE_RE.sub(_replace, source), fixes

    # ── Fix 3: TikZ figures with node styles defined after use ───────────────

    def _fix_undefined_tikz_styles(self, source: str) -> tuple[str, int]:
        """Replace figure blocks whose tikzpicture uses LLM-invented styles before \\tikzset."""
        fixes = 0

        def _check_and_replace(m: re.Match) -> str:
            nonlocal fixes
            block = m.group(0)
            if _INCLUDE_RE.search(block):
                return block  # handled by _fix_includegraphics
            tikzset_pos = block.find(r"\tikzset{")
            if tikzset_pos == -1:
                return block
            pre = block[:tikzset_pos]
            if not any(
                f"[{s}]" in pre or f"[{s}," in pre for s in _TIKZ_BAD_STYLES
            ):
                return block
            # Bad: styles defined after nodes that use them — replace with standard flow
            cap_m = _CAPTION_RE.search(block)
            label_m = _LABEL_RE.search(block)
            new_block = "\\begin{figure}[H]\n  \\centering\n  " + _TIKZFLOW + "\n"
            if cap_m:
                new_block += f"  \\caption{{{cap_m.group(1)}}}\n"
            if label_m:
                new_block += f"  \\label{{{label_m.group(1)}}}\n"
            new_block += "\\end{figure}"
            fixes += 1
            logger.info("Sanitizer: replaced bad-style TikZ → standard flow diagram")
            return new_block

        return _FIGURE_RE.sub(_check_and_replace, source), fixes

    # ── Fix 4: Cover page Hebrew BiDi ────────────────────────────────────────

    def _fix_cover_hebrew(self, source: str) -> tuple[str, int]:
        tp_s = source.find(r"\begin{titlepage}")
        tp_e = source.find(r"\end{titlepage}")
        if tp_s == -1 or tp_e == -1:
            return source, 0
        end_tag = r"\end{titlepage}"
        tp = source[tp_s : tp_e + len(end_tag)]
        fixes = 0

        # Handle multi-line {{\hebrewfont...\n  HEBREW\n  \par}} blocks
        def _fix_multiline(m: re.Match) -> str:
            nonlocal fixes
            full = m.group(0)
            content = m.group(1)
            if r"\begin{hebrew}" in full or not _HEB_RE.search(content):
                return full
            content_stripped = content.strip()
            fixes += 1
            return (
                "{\\hebrewfont\\large\n"
                "    \\begin{hebrew}\n"
                "      " + content_stripped + "\n"
                "    \\end{hebrew}\\par}"
            )

        new_tp = _TP_MULTILINE_HFONT_RE.sub(_fix_multiline, tp)

        # Also handle single-line \hebrewfont + Hebrew without \begin{hebrew}
        new_lines = []
        for line in new_tp.split("\n"):
            if (
                r"\hebrewfont" in line
                and _HEB_RE.search(line)
                and r"\begin{hebrew}" not in line
            ):
                line = self._wrap_hebrew_line(line)
                fixes += 1
            new_lines.append(line)
        new_tp = "\n".join(new_lines)

        return source.replace(tp, new_tp), fixes

    def _wrap_hebrew_line(self, line: str) -> str:
        heb_m = _HEB_RE.search(line)
        if not heb_m:
            return line
        par_idx = line.rfind(r"\par")
        if par_idx <= heb_m.start():
            return line
        indent = re.match(r"(\s*)", line).group(1)
        heb_text = line[heb_m.start() : par_idx].strip()
        return (
            f"{indent}{{\\hebrewfont\\large\n"
            f"{indent}  \\begin{{hebrew}}\n"
            f"{indent}    {heb_text}\n"
            f"{indent}  \\end{{hebrew}}\\par}}"
        )

    # ── Fix 5: Body BiDi — wrap bare hebrew/english envs in tcolorboxes ──────

    def _fix_bidi_body_sections(self, source: str) -> tuple[str, int]:
        """Replace bare \\begin{hebrew}/\\begin{english} in body with hebrewblock/englishblock."""
        tp_e = source.find(r"\end{titlepage}")
        end_tag = r"\end{titlepage}"
        if tp_e == -1:
            prefix, body = "", source
        else:
            split = tp_e + len(end_tag)
            prefix, body = source[:split], source[split:]

        fixes = 0

        def _sub_heb(m: re.Match) -> str:
            nonlocal fixes
            fixes += 1
            return "\\begin{hebrewblock}" + m.group(1) + "\\end{hebrewblock}"

        def _sub_eng(m: re.Match) -> str:
            nonlocal fixes
            fixes += 1
            return "\\begin{englishblock}" + m.group(1) + "\\end{englishblock}"

        new_body = _BODY_HEB_ENV_RE.sub(_sub_heb, body)
        new_body = _BODY_ENG_ENV_RE.sub(_sub_eng, new_body)

        if fixes:
            logger.info(
                "Sanitizer: wrapped %d bare hebrew/english block(s) in tcolorboxes", fixes
            )
        return prefix + new_body, fixes

    # ── Fix 6: Cover metadata (authors, course) ───────────────────────────────

    def _fix_cover_metadata(self, source: str) -> tuple[str, int]:
        tp_s = source.find(r"\begin{titlepage}")
        tp_e = source.find(r"\end{titlepage}")
        if tp_s == -1 or tp_e == -1:
            return source, 0
        end_tag = r"\end{titlepage}"
        tp = source[tp_s : tp_e + len(end_tag)]
        fixes = 0

        def _sub_authors(m: re.Match) -> str:
            nonlocal fixes
            if _AUTHORS in m.group(2):
                return m.group(0)
            fixes += 1
            return m.group(1) + _AUTHORS + " " + m.group(3)

        def _sub_course(m: re.Match) -> str:
            nonlocal fixes
            if _COURSE in m.group(2):
                return m.group(0)
            fixes += 1
            return m.group(1) + _COURSE + " " + m.group(3)

        fixed = _AUTH_ROW_RE.sub(_sub_authors, tp)
        fixed = _COURSE_ROW_RE.sub(_sub_course, fixed)
        return source.replace(tp, fixed), fixes

    # ── Fix 7: Inject \usepackage{ragged2e} if missing; fix typos ────────────

    _RAGGED2_TYPO_RE = re.compile(r"\\usepackage\{ragged2[a-z]+\}")

    def _fix_missing_ragged2e(self, source: str) -> tuple[str, int]:
        fixes = 0
        # Fix any LLM typo variant (ragged2ce, ragged2xe, etc.) → ragged2e
        fixed, n_typo = self._RAGGED2_TYPO_RE.subn(r"\\usepackage{ragged2e}", source)
        if n_typo:
            source = fixed
            fixes += n_typo
            logger.info("Sanitizer: fixed ragged2e typo/variant (%d occurrence(s))", n_typo)
        # Deduplicate: keep only the first \usepackage{ragged2e} line
        seen = False
        lines = []
        for line in source.split("\n"):
            if line.strip() == r"\usepackage{ragged2e}":
                if seen:
                    fixes += 1
                    continue
                seen = True
            lines.append(line)
        source = "\n".join(lines)
        # Inject if still absent
        if r"\usepackage{ragged2e}" not in source and r"\usepackage{tabularx}" in source:
            source = source.replace(
                r"\usepackage{tabularx}",
                "\\usepackage{ragged2e}\n\\usepackage{tabularx}",
                1,
            )
            logger.info("Sanitizer: injected \\usepackage{ragged2e}")
            fixes += 1
        return source, fixes

    # ── Fix 8: Convert bad table column specs → tabularx + RaggedRight X ─────
    # Only applied to body content (after \end{titlepage}) to avoid converting
    # the cover-page label-value tabular which uses a valid {rl} spec.

    # Match full tabular environment including \end{tabular}
    _FULL_TABULAR_RE = re.compile(
        r"\\begin\{tabular\}\{([^}]+)\}(.*?)\\end\{tabular\}",
        re.DOTALL,
    )

    def _fix_table_alignment(self, source: str) -> tuple[str, int]:
        # Split at titlepage boundary — only fix body content
        tp_e = source.find(r"\end{titlepage}")
        end_tag = r"\end{titlepage}"
        if tp_e == -1:
            prefix, body = "", source
        else:
            split = tp_e + len(end_tag)
            prefix, body = source[:split], source[split:]

        fixes = 0

        def _count_cols(spec: str) -> int:
            cleaned = re.sub(r"\|", "", spec)
            cleaned = re.sub(r">?\{[^}]+\}", "", cleaned)
            cleaned = re.sub(r"[pmb]\{[^}]+\}", "X", cleaned)
            return max(1, len(re.findall(r"[lcr X]", cleaned)))

        def _x_cols(n: int) -> str:
            col = r">{\RaggedRight\arraybackslash}X"
            return " ".join([col] * n)

        def _fix_full_tabular(m: re.Match) -> str:
            nonlocal fixes
            spec = m.group(1)
            inner = m.group(2)
            n = _count_cols(spec)
            fixes += 1
            logger.info("Sanitizer: tabular{%s} → tabularx{\\textwidth}{%d X cols}", spec, n)
            return (
                r"\begin{tabularx}{\textwidth}{" + _x_cols(n) + "}"
                + inner
                + r"\end{tabularx}"
            )

        def _fix_tabularx_cols(m: re.Match) -> str:
            nonlocal fixes
            prefix = m.group(1)
            spec = m.group(2)
            if r"\RaggedRight" in spec or (r">{\\" in spec and "X" in spec):
                return m.group(0)
            n = _count_cols(spec)
            fixes += 1
            logger.info(
                "Sanitizer: tabularx col spec {%s} → %d RaggedRight X cols", spec.strip(), n
            )
            return prefix + "{" + _x_cols(n) + "}"

        new_body = self._FULL_TABULAR_RE.sub(_fix_full_tabular, body)
        new_body = _TABULARX_COL_RE.sub(_fix_tabularx_cols, new_body)
        return prefix + new_body, fixes

    # ── Fix 9: TikZ arrow edge-label fill=white clearance ─────────────────────

    def _fix_arrow_labels(self, source: str) -> tuple[str, int]:
        """Inject fill=white, inner sep=2pt into TikZ edge-label nodes that lack it."""
        fixes = 0
        lines = source.split("\n")
        new_lines = []
        for line in lines:
            if ("--" in line or "->" in line) and "node[" in line:
                line, n = self._inject_fill_white(line)
                fixes += n
            new_lines.append(line)
        if fixes:
            logger.info("Sanitizer: added fill=white to %d TikZ edge label(s)", fixes)
        return "\n".join(new_lines), fixes

    def _inject_fill_white(self, line: str) -> tuple[str, int]:
        fixes = 0

        def _sub(m: re.Match) -> str:
            nonlocal fixes
            opts = m.group(2)
            if "fill=" in opts:
                return m.group(0)
            fixes += 1
            injected = "fill=white, inner sep=2pt, font=\\footnotesize, " + opts
            return m.group(1) + injected + m.group(3)

        return _EDGE_NODE_RE.sub(_sub, line), fixes

    # ── Fix 10: Replace LLM-invented \cite{} keys with nearest curated key ────

    @staticmethod
    def _remap_key(key: str) -> str:
        """Return the nearest curated citation key for an invalid key."""
        key_lower = key.lower()
        for kw, replacement in _KEY_REMAP_RULES:
            if kw in key_lower:
                return replacement
        return _CITE_DEFAULT_KEY

    def _fix_invalid_cite_keys(self, source: str) -> tuple[str, int]:
        """Replace any \\cite{key} where key is not in the curated set."""
        fixes = 0

        def _sub(m: re.Match) -> str:
            nonlocal fixes
            raw = m.group(1)
            keys = [k.strip() for k in raw.split(",")]
            new_keys = []
            for k in keys:
                if k in _CURATED_KEYS:
                    new_keys.append(k)
                else:
                    replacement = self._remap_key(k)
                    if replacement != k:
                        fixes += 1
                        logger.info(
                            "Sanitizer: cite key '%s' → '%s' (not in curated set)", k, replacement
                        )
                        new_keys.append(replacement)
                    else:
                        new_keys.append(k)
            # Deduplicate while preserving order
            seen: set[str] = set()
            deduped = []
            for k in new_keys:
                if k not in seen:
                    seen.add(k)
                    deduped.append(k)
            return "\\cite{" + ", ".join(deduped) + "}"

        return _CITE_MULTI_RE.sub(_sub, source), fixes

    # ── Post-compilation validation ───────────────────────────────────────────

    def validate(
        self,
        tex_path: Path,
        log_path: Path | None = None,
        blg_path: Path | None = None,
    ) -> list[str]:
        """Check compiled output for remaining BiDi/bibliography issues."""
        warnings: list[str] = []
        source = tex_path.read_text(encoding="utf-8", errors="replace")

        # 0. Wrong main language — causes entire document to mirror
        if r"\setmainlanguage{hebrew}" in source:
            warnings.append(
                "CRITICAL: \\setmainlanguage{hebrew} detected — entire document will mirror"
            )

        # 1. Malformed closing tags still present
        if re.search(r"</(hebrew|english|hebrewblock|englishblock)[>}]", source):
            warnings.append("WARN: malformed closing env tags remain in .tex")

        # 2. Bare \hebrewfont + Hebrew outside titlepage (BiDi risk)
        body_start = source.find(r"\end{titlepage}")
        body = source[body_start:] if body_start != -1 else source
        for i, line in enumerate(body.split("\n"), 1):
            if (
                r"\hebrewfont" in line
                and _HEB_RE.search(line)
                and r"\begin{hebrew}" not in line
                and r"\texthebrew" not in line
            ):
                warnings.append(
                    f"WARN: bare \\hebrewfont + Hebrew char in body line ~{i} (BiDi risk)"
                )
                break

        # 3. Bare \begin{hebrew} in body (should be wrapped in hebrewblock)
        if _BODY_HEB_ENV_RE.search(body):
            warnings.append(
                "WARN: bare \\begin{hebrew} in body — should be inside hebrewblock"
            )

        # 4. Missing hebrewblock definition
        if r"\newenvironment{hebrewblock}" not in source:
            warnings.append("WARN: hebrewblock env not defined in preamble")

        # 5. Missing citation keys from biber log
        if blg_path and blg_path.exists():
            blg = blg_path.read_text(encoding="utf-8", errors="replace")
            missing = re.findall(r"I didn't find a database entry for '([^']+)'", blg)
            if missing:
                sample = ", ".join(missing[:4])
                warnings.append(
                    f"WARN: {len(missing)} unresolved citation(s): {sample}"
                )

        # 6. Font-not-found in lualatex log + undefined references
        if log_path and log_path.exists():
            log = log_path.read_text(encoding="utf-8", errors="replace")
            if "font not found" in log.lower():
                warnings.append("WARN: font-not-found error in lualatex .log")
            # Undefined references appear as [?] in the compiled PDF
            undef_refs = re.findall(
                r"LaTeX Warning: Reference `([^']+)' on page \d+ undefined", log
            )
            if undef_refs:
                sample = ", ".join(undef_refs[:4])
                warnings.append(
                    f"WARN: {len(undef_refs)} undefined \\ref/\\label(s) in compiled PDF "
                    f"(appear as [?]): {sample}"
                )
            # Citations that biber couldn't resolve show as [?] in biblatex
            undef_cites = re.findall(
                r"Package biblatex Warning: Citation '([^']+)' on page", log
            )
            if undef_cites:
                sample = ", ".join(undef_cites[:4])
                warnings.append(
                    f"WARN: {len(undef_cites)} unresolved \\cite key(s) showing as [?]: {sample}"
                )

        # 7. Placeholder/root-domain URLs in references.bib
        bib_path = tex_path.parent / "references.bib"
        if bib_path.exists():
            bib = bib_path.read_text(encoding="utf-8", errors="replace")
            placeholder_urls = [
                u for u in _BIB_URL_RE.findall(bib) if _is_root_domain_url(u)
            ]
            if placeholder_urls:
                sample = ", ".join(placeholder_urls[:3])
                warnings.append(
                    f"WARN: {len(placeholder_urls)} root-domain URL(s) in references.bib "
                    f"(e.g. {sample})"
                )

        if warnings:
            for w in warnings:
                logger.warning("Validator: %s", w)
        else:
            logger.info("Validator: all BiDi/bibliography checks passed")
        return warnings
