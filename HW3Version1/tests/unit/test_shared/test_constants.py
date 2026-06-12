"""Unit tests for shared/constants.py."""
from article_writer.shared import constants


def test_confidence_values_are_strings() -> None:
    assert isinstance(constants.CONFIDENCE_HIGH, str)
    assert isinstance(constants.CONFIDENCE_MEDIUM, str)
    assert isinstance(constants.CONFIDENCE_LOW, str)


def test_confidence_values_are_distinct() -> None:
    vals = {constants.CONFIDENCE_HIGH, constants.CONFIDENCE_MEDIUM, constants.CONFIDENCE_LOW}
    assert len(vals) == 3


def test_path_constants_non_empty() -> None:
    assert constants.RESEARCH_ARTIFACT_PATH
    assert constants.GUIDELINE_PATH
    assert constants.PROFILES_DIR
    assert constants.FEW_SHOT_DIR
    assert constants.RESULTS_DIR


def test_numeric_constants() -> None:
    assert constants.MAX_FILE_LINES == 150
    assert constants.MIN_ARTICLE_PAGES == 15
    assert constants.MAX_SANITIZE_CHARS > 0


def test_version_fallback_format() -> None:
    parts = constants.VERSION_FALLBACK.split(".")
    assert len(parts) == 2
    assert parts[0].isdigit()
    assert parts[1].isdigit()
