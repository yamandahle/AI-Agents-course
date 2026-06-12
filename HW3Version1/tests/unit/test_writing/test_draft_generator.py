"""Tests for writing/draft_generator.py — generates initial LaTeX draft."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from article_writer.shared.config import AppConfig, LLMConfig, ResearchConfig, WritingConfig, LaTeXConfig


def _fake_config() -> AppConfig:
    return AppConfig(
        version="1.0",
        llm=LLMConfig(provider="anthropic", model="claude-sonnet-4-6", temperature=0.3),
        research=ResearchConfig(search_backend="gemini", fallback_backend="perplexity",
                                batch_size=5, max_batches=3, min_confidence="MEDIUM"),
        writing=WritingConfig(max_evaluator_iterations=3, score_threshold=8.0, target_pages=15),
        latex=LaTeXConfig(compiler="lualatex", compile_passes=4),
    )


_VALID_TEX = r"\documentclass{article}\begin{document}\maketitle\tableofcontents Hello\end{document}"


def _mock_response(tex: str = _VALID_TEX) -> MagicMock:
    resp = MagicMock()
    resp.content = [MagicMock(text=tex)]
    resp.usage.input_tokens = 100
    resp.usage.output_tokens = 200
    return resp


def test_generate_saves_draft_v1(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from article_writer.writing.draft_generator import DraftGenerator
    with patch("article_writer.writing.draft_generator.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_response()
        gen = DraftGenerator("context", config=_fake_config())
        result = gen.generate()
    assert result.name == "draft_v1.tex"
    assert result.exists()


def test_validate_raises_on_missing_begin_document(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from article_writer.writing.draft_generator import DraftGenerator
    bad_tex = r"\documentclass{article}\maketitle\tableofcontents\end{document}"
    with patch("article_writer.writing.draft_generator.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_response(bad_tex)
        gen = DraftGenerator("context", config=_fake_config())
        with pytest.raises(ValueError, match=r"\\begin\{document\}"):
            gen.generate()


def test_generate_file_content_matches_llm_response(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from article_writer.writing.draft_generator import DraftGenerator
    with patch("article_writer.writing.draft_generator.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = _mock_response()
        gen = DraftGenerator("context", config=_fake_config())
        result = gen.generate()
    assert r"\begin{document}" in result.read_text(encoding="utf-8")
