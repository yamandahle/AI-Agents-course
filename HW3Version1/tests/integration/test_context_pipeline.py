"""Integration test — ContextLoader → DraftGenerator (with mock LLM)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch


def _write_context_files(tmp_path: Path) -> dict:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "guideline.md").write_text("## Topic\nAI in Healthcare\n", encoding="utf-8")
    (tmp_path / "data" / "research.md").write_text("# Research\n- Fact 1 — [Source](http://x.com)\n", encoding="utf-8")
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    for name in ("Structure.md", "Terminology.md", "Characters.md"):
        (profiles / name).write_text(f"# {name}\nRules.", encoding="utf-8")
    (tmp_path / "few_shot_examples").mkdir()
    return {
        "guideline": str(tmp_path / "data" / "guideline.md"),
        "research": str(tmp_path / "data" / "research.md"),
        "profiles": str(profiles),
        "few_shots": str(tmp_path / "few_shot_examples"),
    }


def test_context_loader_builds_non_empty_context(tmp_path: Path) -> None:
    from article_writer.writing.context_loader import ContextLoader
    paths = _write_context_files(tmp_path)
    loader = ContextLoader(
        guideline_path=paths["guideline"],
        research_path=paths["research"],
        profiles_dir=paths["profiles"],
        few_shot_dir=paths["few_shots"],
    )
    ctx = loader.build_writer_context()
    assert len(ctx) > 100
    assert "AI in Healthcare" in ctx
    assert "Fact 1" in ctx


def test_draft_generator_saves_file(tmp_path: Path, monkeypatch) -> None:
    from article_writer.shared.config import AppConfig, LLMConfig, ResearchConfig, WritingConfig, LaTeXConfig
    from article_writer.writing.draft_generator import DraftGenerator

    fake_tex = r"\documentclass{article}\begin{document}\maketitle\tableofcontents\end{document}"
    fake_config = AppConfig(
        version="1.0",
        llm=LLMConfig(provider="anthropic", model="claude-sonnet-4-6", temperature=0.3),
        research=ResearchConfig(search_backend="gemini", fallback_backend="perplexity",
                                batch_size=5, max_batches=3, min_confidence="MEDIUM"),
        writing=WritingConfig(max_evaluator_iterations=3, score_threshold=8.0, target_pages=15),
        latex=LaTeXConfig(compiler="lualatex", compile_passes=4),
    )
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text=fake_tex)]
    mock_resp.usage.input_tokens = 10
    mock_resp.usage.output_tokens = 20

    monkeypatch.chdir(tmp_path)
    with patch("article_writer.writing.draft_generator.load_config", return_value=fake_config), \
         patch("article_writer.writing.draft_generator.ApiGatekeeper") as MockGate:
        MockGate.return_value.execute.return_value = mock_resp
        gen = DraftGenerator("test context", config=fake_config)
        result = gen.generate()
    assert result.exists()
    assert result.name == "draft_v1.tex"
