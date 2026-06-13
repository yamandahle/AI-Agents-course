"""Tests for sdk/sdk.py — ArticleWriterSDK facade."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from article_writer.sdk.sdk import ArticleWriterSDK


def _sdk() -> ArticleWriterSDK:
    mock_cfg = MagicMock()
    mock_cfg.writing.review_iterations = 3
    with patch("article_writer.sdk.sdk.load_config", return_value=mock_cfg):
        return ArticleWriterSDK()


# ── _extract_topic ────────────────────────────────────────────────────────────

def test_extract_topic_from_header(tmp_path: Path) -> None:
    g = tmp_path / "guideline.md"
    g.write_text("# Article Guideline — AI in Healthcare\n\nSome content.", encoding="utf-8")
    sdk = _sdk()
    assert sdk._extract_topic(str(g)) == "AI in Healthcare"


def test_extract_topic_falls_back_to_first_line(tmp_path: Path) -> None:
    g = tmp_path / "guideline.md"
    g.write_text("## Topic\nArtificial Intelligence in Medicine.", encoding="utf-8")
    sdk = _sdk()
    result = sdk._extract_topic(str(g))
    assert len(result) > 0


def test_extract_topic_guideline_no_dash(tmp_path: Path) -> None:
    g = tmp_path / "guideline.md"
    g.write_text("# Article Guideline\nSome content.", encoding="utf-8")
    sdk = _sdk()
    result = sdk._extract_topic(str(g))
    assert len(result) > 0


# ── generate_guideline ────────────────────────────────────────────────────────
# sdk.generate_guideline does: from article_writer.writing.guideline_generator import GuidelineGenerator

def test_generate_guideline_calls_generator(tmp_path: Path) -> None:
    sdk = _sdk()
    mock_path = tmp_path / "guideline.md"
    mock_gen_instance = MagicMock()
    mock_gen_instance.generate.return_value = mock_path
    with patch("article_writer.writing.guideline_generator.GuidelineGenerator",
               return_value=mock_gen_instance):
        result = sdk.generate_guideline("AI in Healthcare", str(mock_path))
    assert result == mock_path


# ── start_writing_session ─────────────────────────────────────────────────────

def test_start_writing_session_returns_path(tmp_path: Path) -> None:
    sdk = _sdk()
    expected = tmp_path / "draft_v1.tex"
    mock_loader = MagicMock()
    mock_loader.build_writer_context.return_value = "context text"
    mock_gen = MagicMock()
    mock_gen.generate.return_value = expected
    with patch("article_writer.writing.context_loader.ContextLoader",
               return_value=mock_loader), \
         patch("article_writer.writing.draft_generator.DraftGenerator",
               return_value=mock_gen):
        result = sdk.start_writing_session(
            guideline_path="data/guideline.md",
            research_path="data/research.md",
        )
    assert result == expected


# ── run_review_loop ────────────────────────────────────────────────────────────

def test_run_review_loop_returns_final_path(tmp_path: Path) -> None:
    sdk = _sdk()
    final = tmp_path / "draft_final.tex"
    mock_loop = MagicMock()
    mock_loop.run.return_value = final
    with patch("article_writer.writing.review_loop.ReviewLoop",
               return_value=mock_loop), \
         patch("article_writer.shared.llm_client.LLMClient"):
        result = sdk.run_review_loop("results/draft_v1.tex", iterations=2)
    assert result == final


def test_run_evaluator_loop_delegates_to_review_loop() -> None:
    sdk = _sdk()
    with patch.object(sdk, "run_review_loop", return_value=Path("draft_final.tex")) as mock_rl:
        result = sdk.run_evaluator_loop("results/draft_v1.tex", max_iter=3)
    mock_rl.assert_called_once_with("results/draft_v1.tex", 3)


# ── compile_to_pdf ────────────────────────────────────────────────────────────

def test_compile_to_pdf_calls_sanitizer_and_compiler(tmp_path: Path) -> None:
    sdk = _sdk()
    tex_path = tmp_path / "results" / "draft.tex"
    tex_path.parent.mkdir(parents=True)
    tex_path.write_text(r"\documentclass{article}\begin{document}\end{document}", encoding="utf-8")
    bib_path = tmp_path / "results" / "references.bib"
    bib_path.write_text("", encoding="utf-8")
    pdf_out = tmp_path / "results" / "article_final.pdf"
    pdf_out.write_bytes(b"%PDF-1.4")

    mock_san = MagicMock()
    mock_san.sanitize.return_value = tex_path
    mock_san.validate.return_value = []
    mock_comp = MagicMock()
    mock_comp.compile.return_value = pdf_out

    with patch("article_writer.latex.latex_sanitizer.LatexSanitizer",
               return_value=mock_san), \
         patch("article_writer.latex.latex_compiler.LaTeXCompiler",
               return_value=mock_comp):
        result = sdk.compile_to_pdf(str(tex_path))

    mock_san.sanitize.assert_called_once()
    mock_comp.compile.assert_called_once()
