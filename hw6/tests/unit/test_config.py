"""Unit tests for the shared config loader — TDD red phase."""

import pytest

from cop_thief.shared.config import load_config


def test_load_config_returns_dict():
    config = load_config("config.json")
    assert isinstance(config, dict)


def test_load_config_contains_llm_section():
    config = load_config("config.json")
    assert config["llm"]["provider"] == "ollama"
    assert config["llm"]["model"] == "phi3:mini"


def test_load_config_contains_version():
    config = load_config("config.json")
    assert config["version"] == "1.0"


def test_load_config_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_config("does_not_exist.json")
