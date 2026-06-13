"""Tests for tools/chart_checker.py — zero-API LaTeX chart self-check."""
from __future__ import annotations

from article_writer.tools.chart_checker import (
    _tex_safe,
    check_alignment,
    extract_draft_figure,
    extract_research_facts,
)


# ── _tex_safe ─────────────────────────────────────────────────────────────────

def test_tex_safe_escapes_ampersand() -> None:
    assert _tex_safe("A & B") == r"A \& B"


def test_tex_safe_escapes_percent() -> None:
    assert _tex_safe("50%") == r"50\%"


def test_tex_safe_escapes_hash() -> None:
    assert _tex_safe("C#") == r"C\#"


def test_tex_safe_escapes_underscore() -> None:
    assert _tex_safe("my_var") == r"my\_var"


def test_tex_safe_escapes_dollar() -> None:
    assert _tex_safe("$100") == r"\$100"


def test_tex_safe_plain_text_unchanged() -> None:
    assert _tex_safe("Hello World") == "Hello World"


# ── extract_draft_figure ──────────────────────────────────────────────────────

_SAMPLE_AXIS = r"""
\begin{figure}[H]
Some prose about Mammography Screening and Drug Detection.

\begin{tikzpicture}
\begin{axis}[ybar,
  ylabel={Accuracy (\%)},
  xlabel={Task},
  xtick=data,
  symbolic x coords={Mammography Screening,Drug Detection,Pathology},
]
  \addplot+[fill=blue!60] coordinates {(Mammography Screening,94)(Drug Detection,90)(Pathology,91)};
  \addplot+[fill=orange!60] coordinates {(Mammography Screening,85)(Drug Detection,87)(Pathology,86)};
  \legend{AI Agent,Human Expert}
\end{axis}
\end{tikzpicture}
\caption{Accuracy comparison.\cite{who2021ai}}
\end{figure}
"""


def test_extract_draft_figure_finds_tick_labels() -> None:
    result = extract_draft_figure(_SAMPLE_AXIS)
    assert "Mammography Screening" in result["tick_labels"]
    assert "Drug Detection" in result["tick_labels"]
    assert "Pathology" in result["tick_labels"]


def test_extract_draft_figure_finds_series() -> None:
    result = extract_draft_figure(_SAMPLE_AXIS)
    names = [s["name"] for s in result["series"]]
    assert "AI Agent" in names
    assert "Human Expert" in names


def test_extract_draft_figure_returns_empty_on_no_axis() -> None:
    result = extract_draft_figure("no axis here")
    assert result == {}


def test_extract_draft_figure_ylabel() -> None:
    result = extract_draft_figure(_SAMPLE_AXIS)
    assert "Accuracy" in result["ylabel"]


# ── check_alignment ───────────────────────────────────────────────────────────

def test_check_alignment_pass_when_label_in_context() -> None:
    data = {
        "tick_labels": ["Mammography Screening"],
        "context": "We studied Mammography Screening outcomes.",
    }
    results = check_alignment(data)
    assert results == [("Mammography Screening", True)]


def test_check_alignment_fail_when_label_absent() -> None:
    data = {
        "tick_labels": ["Pathology"],
        "context": "We studied mammography and drug detection.",
    }
    results = check_alignment(data)
    assert results == [("Pathology", False)]


def test_check_alignment_empty_data() -> None:
    assert check_alignment({}) == []


def test_check_alignment_mixed() -> None:
    data = {
        "tick_labels": ["In Context", "Not Here"],
        "context": "In Context appears in the prose.",
    }
    results = dict(check_alignment(data))
    assert results["In Context"] is True
    assert results["Not Here"] is False


# ── extract_research_facts ────────────────────────────────────────────────────

def test_extract_research_facts_finds_denial_reduction() -> None:
    md = "- **Fact**: AI reduced prior authorization denials by 67% denial reduction in study.\n"
    facts = extract_research_facts(md)
    labels = [f[0] for f in facts]
    assert "Denial Rate Reduction" in labels


def test_extract_research_facts_finds_drug_alert() -> None:
    md = "- **Fact**: System reduced drug interaction alerts by 52% in hospital.\n"
    facts = extract_research_facts(md)
    labels = [f[0] for f in facts]
    assert "Drug Alert Reduction" in labels


def test_extract_research_facts_empty_md() -> None:
    assert extract_research_facts("") == []


def test_extract_research_facts_no_matching_facts() -> None:
    md = "- **Fact**: This is an unrelated sentence about weather.\n"
    facts = extract_research_facts(md)
    assert facts == []
