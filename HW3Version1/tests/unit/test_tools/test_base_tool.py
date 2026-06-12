"""Unit tests for tools/base_tool.py."""
from article_writer.tools.base_tool import ArticleBaseTool


class _ConcreteTool(ArticleBaseTool):
    name: str = "test_tool"
    description: str = "Test tool."

    def _run(self, prompt: str) -> str:
        return self._sanitize_input(prompt)


def test_sanitize_strips_html_tags() -> None:
    tool = _ConcreteTool()
    result = tool._sanitize_input("<b>bold</b> text")
    assert "<b>" not in result
    assert "bold" in result


def test_sanitize_strips_script_tags() -> None:
    tool = _ConcreteTool()
    result = tool._sanitize_input("<script>alert(1)</script>safe")
    assert "alert" not in result
    assert "safe" in result


def test_sanitize_truncates_to_max_chars() -> None:
    from article_writer.shared.constants import MAX_SANITIZE_CHARS
    tool = _ConcreteTool()
    long_text = "a" * (MAX_SANITIZE_CHARS + 100)
    result = tool._sanitize_input(long_text)
    assert len(result) == MAX_SANITIZE_CHARS


def test_format_markdown_output_starts_with_header() -> None:
    tool = _ConcreteTool()
    result = tool._format_markdown_output("Test Header", "body text")
    assert result.startswith("## Test Header")


def test_log_call_does_not_raise() -> None:
    tool = _ConcreteTool()
    tool._log_call("some input")
