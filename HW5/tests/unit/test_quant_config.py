"""T078–T081: Tests for QuantizationConfig."""

from __future__ import annotations

import pytest

from hw5.shared.quant_config import QuantizationConfig


# T078 — all valid labels
@pytest.mark.parametrize(
    "label,expected_bits",
    [
        ("Q2", 2),
        ("Q4", 4),
        ("Q8", 8),
    ],
)
def test_from_label_valid(label, expected_bits):
    q = QuantizationConfig.from_label(label)
    assert q.label == label
    assert q.bits == expected_bits


def test_from_label_lowercase_normalised():
    q = QuantizationConfig.from_label("q4")
    assert q.label == "Q4"
    assert q.bits == 4


# T079 — invalid label
def test_from_label_invalid_raises():
    with pytest.raises(ValueError, match="Unknown quantization label"):
        QuantizationConfig.from_label("Q16")


def test_from_label_empty_string_raises():
    with pytest.raises(ValueError):
        QuantizationConfig.from_label("")


def test_validate_passes_for_valid_bits():
    q = QuantizationConfig(bits=4, label="Q4")
    q.validate()  # must not raise


def test_validate_raises_for_unsupported_bits():
    q = QuantizationConfig(bits=6, label="Q6")
    with pytest.raises(ValueError, match="Unsupported quantization bits"):
        q.validate()


# T080 — to_ollama_tag
def test_to_ollama_tag_q4():
    assert QuantizationConfig.from_label("Q4").to_ollama_tag() == "q4_K_M"


def test_to_ollama_tag_q8():
    assert QuantizationConfig.from_label("Q8").to_ollama_tag() == "q8_0"


def test_to_ollama_tag_q2():
    assert QuantizationConfig.from_label("Q2").to_ollama_tag() == "q2_K"


# T081 — to_airllm_param
def test_to_airllm_param_q4():
    assert QuantizationConfig.from_label("Q4").to_airllm_param() == "4bit"


def test_to_airllm_param_q8():
    assert QuantizationConfig.from_label("Q8").to_airllm_param() == "8bit"


def test_to_airllm_param_q2():
    assert QuantizationConfig.from_label("Q2").to_airllm_param() == "2bit"


# T076/T077 — str and repr
def test_str_returns_label():
    q = QuantizationConfig.from_label("Q4")
    assert str(q) == "Q4"


def test_repr_contains_bits_and_label():
    q = QuantizationConfig.from_label("Q8")
    r = repr(q)
    assert "bits=8" in r
    assert "Q8" in r


def test_frozen_dataclass_is_hashable():
    q = QuantizationConfig.from_label("Q4")
    d = {q: "value"}
    assert d[q] == "value"
