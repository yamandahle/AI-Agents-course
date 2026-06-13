"""Tests for writing/guideline_generator.py — LLM-powered guideline expansion."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from article_writer.writing.guideline_generator import GuidelineGenerator
from article_writer.shared.llm_client import LLMResponse


def _mock_llm(text: str = "# Article Guideline — AI\n\n## Topic\nAI content.") -> MagicMock:
    llm = MagicMock()
    llm.complete.return_value = LLMResponse(
        text=text, input_tokens=50, output_tokens=100, model="mock", cost_usd=0.0
    )
    return llm


def test_generate_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "guideline.md"
    gen = GuidelineGenerator(llm=_mock_llm())
    result = gen.generate("AI in Healthcare", str(out))
    assert result == out
    assert out.exists()
    assert "Article Guideline" in out.read_text(encoding="utf-8")


def test_generate_returns_path(tmp_path: Path) -> None:
    out = tmp_path / "guideline.md"
    gen = GuidelineGenerator(llm=_mock_llm())
    result = gen.generate("Robotics", str(out))
    assert isinstance(result, Path)


def test_generate_strips_whitespace(tmp_path: Path) -> None:
    out = tmp_path / "guideline.md"
    gen = GuidelineGenerator(llm=_mock_llm("  \n# Article Guideline\n\n  "))
    gen.generate("topic", str(out))
    content = out.read_text(encoding="utf-8")
    assert not content.startswith(" ")
    assert not content.startswith("\n")


def test_generate_calls_llm_complete(tmp_path: Path) -> None:
    out = tmp_path / "guideline.md"
    llm = _mock_llm()
    gen = GuidelineGenerator(llm=llm)
    gen.generate("AI topic", str(out))
    llm.complete.assert_called_once()
    call_kwargs = llm.complete.call_args
    assert "AI topic" in str(call_kwargs)


def test_generate_creates_parent_dir(tmp_path: Path) -> None:
    out = tmp_path / "subdir" / "guideline.md"
    gen = GuidelineGenerator(llm=_mock_llm())
    gen.generate("topic", str(out))
    assert out.exists()


def test_guideline_generator_default_llm_uses_llm_client() -> None:
    with patch("article_writer.writing.guideline_generator.LLMClient") as MockLLM:
        MockLLM.return_value = _mock_llm()
        gen = GuidelineGenerator()
    MockLLM.assert_called_once()
