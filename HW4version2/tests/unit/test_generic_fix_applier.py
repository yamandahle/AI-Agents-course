"""Unit tests for GenericFixApplier._parse_response and _resolve_target."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hw4.services.generic_fix_applier import (
    _DELIMITER_MODIFIED,
    _DELIMITER_NEW,
    GenericFixApplier,
)
from hw4.shared.gatekeeper import ApiGatekeeper, RateLimitConfig


def _gatekeeper() -> ApiGatekeeper:
    cfg = RateLimitConfig(60, 1000, 5, 0, 1)
    gk = ApiGatekeeper(config=cfg)
    gk.execute = lambda fn, *a, **kw: fn(*a, **kw)
    return gk


def _applier(tmp_path: Path) -> GenericFixApplier:
    llm = MagicMock()
    llm.complete.return_value = (
        f"{_DELIMITER_MODIFIED}\nmodified content\n{_DELIMITER_NEW}\nnew module content"
    )
    return GenericFixApplier(llm, _gatekeeper(), {"results": str(tmp_path)})


# ── _parse_response ───────────────────────────────────────────────────────────

def test_parse_response_valid(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    response = f"{_DELIMITER_MODIFIED}\nAAA\n{_DELIMITER_NEW}\nBBB"
    modified, new_mod = applier._parse_response(response)
    assert modified == "AAA"
    assert new_mod == "BBB"


def test_parse_response_missing_modified_raises(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    with pytest.raises(ValueError, match="missing required delimiters"):
        applier._parse_response(f"some text\n{_DELIMITER_NEW}\nBBB")


def test_parse_response_missing_new_raises(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    with pytest.raises(ValueError, match="missing required delimiters"):
        applier._parse_response(f"{_DELIMITER_MODIFIED}\nAAA")


def test_parse_response_strips_whitespace(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    response = f"{_DELIMITER_MODIFIED}\n  AAA  \n{_DELIMITER_NEW}\n  BBB  "
    modified, new_mod = applier._parse_response(response)
    assert modified == "AAA"
    assert new_mod == "BBB"


# ── _resolve_target ───────────────────────────────────────────────────────────

def test_resolve_target_existing_path(tmp_path: Path) -> None:
    f = tmp_path / "existing.py"
    f.write_text("x = 1")
    applier = _applier(tmp_path)
    assert applier._resolve_target(f) == f.resolve()


def test_resolve_target_missing_path_raises(tmp_path: Path) -> None:
    applier = _applier(tmp_path)
    missing = tmp_path / "ghost.py"
    with pytest.raises(FileNotFoundError):
        applier._resolve_target(missing)
