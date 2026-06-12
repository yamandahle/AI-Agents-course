"""Tests for writing/optimizer.py — critique-driven LaTeX draft revision."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_VALID_LATEX = r"""\documentclass{article}
\begin{document}
Hello world, this is the revised draft.
\end{document}"""


def _mock_response(text: str) -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_optimize_saves_next_version(tmp_path: Path) -> None:
    draft = tmp_path / "draft_v1.tex"
    critique = tmp_path / "critique_v1.md"
    draft.write_text(r"\begin{document}Old content\end{document}", encoding="utf-8")
    critique.write_text("- Add more examples.", encoding="utf-8")
    mock_msg = _mock_response(_VALID_LATEX)
    with patch("anthropic.Anthropic"), \
         patch("article_writer.writing.optimizer.RESULTS_DIR", str(tmp_path)):
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.optimizer.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.optimizer import Optimizer
            opt = Optimizer(iteration=1)
            out_path = opt.optimize(draft, critique)
    assert out_path.exists()
    assert out_path.name == "draft_v2.tex"
    assert "Hello world" in out_path.read_text(encoding="utf-8")


def test_optimize_raises_on_missing_begin_document(tmp_path: Path) -> None:
    draft = tmp_path / "draft_v1.tex"
    critique = tmp_path / "critique_v1.md"
    draft.write_text(r"\begin{document}Old\end{document}", encoding="utf-8")
    critique.write_text("- Fix structure.", encoding="utf-8")
    bad_latex = r"Just some text without document environment"
    mock_msg = _mock_response(bad_latex)
    with patch("anthropic.Anthropic"), \
         patch("article_writer.writing.optimizer.RESULTS_DIR", str(tmp_path)):
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.optimizer.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.optimizer import Optimizer
            opt = Optimizer(iteration=1)
            with pytest.raises(ValueError, match=r"\\begin\{document\}"):
                opt.optimize(draft, critique)


def test_optimize_raises_on_missing_end_document(tmp_path: Path) -> None:
    draft = tmp_path / "draft_v1.tex"
    critique = tmp_path / "critique_v1.md"
    draft.write_text(r"\begin{document}Old\end{document}", encoding="utf-8")
    critique.write_text("- Fix.", encoding="utf-8")
    bad_latex = r"\begin{document}Content without end"
    mock_msg = _mock_response(bad_latex)
    with patch("anthropic.Anthropic"), \
         patch("article_writer.writing.optimizer.RESULTS_DIR", str(tmp_path)):
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.optimizer.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.optimizer import Optimizer
            opt = Optimizer(iteration=1)
            with pytest.raises(ValueError, match=r"\\end\{document\}"):
                opt.optimize(draft, critique)


def test_optimize_version_increments_with_iteration(tmp_path: Path) -> None:
    draft = tmp_path / "draft_v3.tex"
    critique = tmp_path / "critique_v3.md"
    draft.write_text(r"\begin{document}Draft 3\end{document}", encoding="utf-8")
    critique.write_text("- Improve style.", encoding="utf-8")
    mock_msg = _mock_response(_VALID_LATEX)
    with patch("anthropic.Anthropic"), \
         patch("article_writer.writing.optimizer.RESULTS_DIR", str(tmp_path)):
        mock_gate = MagicMock()
        mock_gate.execute.return_value = mock_msg
        with patch("article_writer.writing.optimizer.ApiGatekeeper", return_value=mock_gate):
            from article_writer.writing.optimizer import Optimizer
            opt = Optimizer(iteration=3)
            out_path = opt.optimize(draft, critique)
    assert out_path.name == "draft_v4.tex"
