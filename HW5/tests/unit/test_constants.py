"""T052: Verify all constants have correct types and non-empty values."""

from __future__ import annotations

from hw5.shared.constants import (
    ASSETS_DIR,
    DEFAULT_MAX_TOKENS,
    DEFAULT_OLLAMA_HOST,
    FRAMEWORK_COLORS,
    QUANT_LINESTYLES,
    QUANT_MARKERS,
    RESULTS_DIR,
    SAMPLE_INTERVAL_S,
    SUPPORTED_QUANT_LEVELS,
    VALID_FRAMEWORKS,
    VRAM_SPIKE_THRESHOLD_MB,
)


def test_sample_interval_is_positive_float():
    assert isinstance(SAMPLE_INTERVAL_S, float)
    assert SAMPLE_INTERVAL_S > 0


def test_vram_spike_threshold_is_positive_float():
    assert isinstance(VRAM_SPIKE_THRESHOLD_MB, float)
    assert VRAM_SPIKE_THRESHOLD_MB > 0


def test_default_max_tokens_is_positive_int():
    assert isinstance(DEFAULT_MAX_TOKENS, int)
    assert DEFAULT_MAX_TOKENS > 0


def test_default_ollama_host_is_string():
    assert isinstance(DEFAULT_OLLAMA_HOST, str)
    assert DEFAULT_OLLAMA_HOST.startswith("http")


def test_supported_quant_levels_is_non_empty_list():
    assert isinstance(SUPPORTED_QUANT_LEVELS, list)
    assert len(SUPPORTED_QUANT_LEVELS) > 0
    assert all(isinstance(q, str) for q in SUPPORTED_QUANT_LEVELS)


def test_supported_quant_levels_contains_q2_q4_q8():
    assert "Q2" in SUPPORTED_QUANT_LEVELS
    assert "Q4" in SUPPORTED_QUANT_LEVELS
    assert "Q8" in SUPPORTED_QUANT_LEVELS


def test_valid_frameworks_contains_ollama_and_airllm():
    assert "ollama" in VALID_FRAMEWORKS
    assert "airllm" in VALID_FRAMEWORKS


def test_framework_colors_has_entry_for_each_framework():
    assert isinstance(FRAMEWORK_COLORS, dict)
    for fw in VALID_FRAMEWORKS:
        assert fw in FRAMEWORK_COLORS
        assert isinstance(FRAMEWORK_COLORS[fw], str)


def test_quant_markers_has_entry_for_each_quant_level():
    assert isinstance(QUANT_MARKERS, dict)
    for q in SUPPORTED_QUANT_LEVELS:
        assert q in QUANT_MARKERS
        assert isinstance(QUANT_MARKERS[q], str)


def test_quant_linestyles_has_entry_for_each_quant_level():
    assert isinstance(QUANT_LINESTYLES, dict)
    for q in SUPPORTED_QUANT_LEVELS:
        assert q in QUANT_LINESTYLES
        assert isinstance(QUANT_LINESTYLES[q], str)


def test_results_and_assets_dir_are_strings():
    assert isinstance(RESULTS_DIR, str)
    assert isinstance(ASSETS_DIR, str)
    assert len(RESULTS_DIR) > 0
    assert len(ASSETS_DIR) > 0
