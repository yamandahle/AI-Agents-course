"""Unit tests for main.py's CLI argument parsing — TDD red phase."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from main import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.gui is False
    assert args.headless is False
    assert args.case is None


def test_parse_args_headless_flag():
    args = parse_args(["--headless"])
    assert args.headless is True


def test_parse_args_gui_flag():
    args = parse_args(["--gui"])
    assert args.gui is True


def test_parse_args_case_flag():
    args = parse_args(["--case", "vision_small"])
    assert args.case == "vision_small"
