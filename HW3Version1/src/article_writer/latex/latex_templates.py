"""LuaLaTeX document templates — preamble, cover page, headers/footers, bibliography."""

LUALATEX_PREAMBLE = r"""\documentclass[12pt,a4paper]{article}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguage{hebrew}
\usepackage{fontspec}
\setmainfont{FreeSerif}
\newfontfamily\hebrewfont[Script=Hebrew]{FreeSans}
\usepackage[a4paper, margin=2.5cm]{geometry}
\usepackage[colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue]{hyperref}
\usepackage[backend=biber, style=ieee]{biblatex}
\addbibresource{references.bib}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{fancyhdr}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
"""

HEADER_FOOTER_SETUP = r"""\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\leftmark}
\fancyhead[R]{\small\thepage}
\fancyfoot[C]{\small AI Agents Course --- \today}
\renewcommand{\headrulewidth}{0.4pt}
"""

COVER_PAGE = r"""\begin{{titlepage}}
  \centering
  \vspace*{{2cm}}
  {{\Huge\bfseries {title}\par}}
  \vspace{{1.5cm}}
  {{\Large {author}\par}}
  \vspace{{0.5cm}}
  {{\large Submitted: {date}\par}}
  {{\large Course: {course}\par}}
  {{\large Lecturer: {lecturer}\par}}
  \vfill
  {{\large \today\par}}
\end{{titlepage}}
"""

BIBLIOGRAPHY_SECTION = r"""
\newpage
\printbibliography[heading=bibintoc, title={Bibliography}]
"""

TOC_SECTION = r"""\newpage
\tableofcontents
\newpage
"""
