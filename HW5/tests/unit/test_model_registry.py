"""T146–T160, T166: Tests for ModelEntry and ModelRegistry."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hw5.services.model_entry import ModelEntry
from hw5.services.model_registry import DownloadError, ModelRegistry, RegistryError
from hw5.shared.gatekeeper import ApiGatekeeper

# ── helpers ──────────────────────────────────────────────────────────────────


def _registry(models_json: Path) -> ModelRegistry:
    gk = ApiGatekeeper(rate=1000.0, burst=100)
    reg = ModelRegistry(gk)
    reg.load_config(str(models_json))
    return reg


def _hook_json(tmp_path: Path) -> Path:
    data = {
        "models": [
            {
                "name": "bad_model",
                "hf_repo_id": "<HOOK: replace me>",
                "ollama_tag": "bad:latest",
                "local_cache": str(tmp_path / "cache"),
                "size_class": "large",
                "param_count_b": 7.0,
                "ollama_compatible": True,
                "airllm_compatible": True,
                "description": "unfinished",
            }
        ]
    }
    p = tmp_path / "hook_models.json"
    p.write_text(json.dumps(data))
    return p


def _empty_json(tmp_path: Path) -> Path:
    p = tmp_path / "empty_models.json"
    p.write_text(json.dumps({"models": []}))
    return p


# ── ModelEntry unit tests ─────────────────────────────────────────────────────


# T157 — invalid size_class raises ValueError
def test_model_entry_invalid_size_class_raises():
    with pytest.raises(ValueError, match="size_class"):
        ModelEntry(
            name="m",
            hf_repo_id="org/m",
            ollama_tag="m:latest",
            local_cache="/tmp/cache",
            size_class="xlarge",
            ollama_compatible=True,
            airllm_compatible=True,
            description="bad size",
        )


def test_model_entry_valid_size_classes():
    for sc in ("small", "large"):
        e = ModelEntry(
            name="m",
            hf_repo_id="org/m",
            ollama_tag="m:latest",
            local_cache="/tmp/cache",
            size_class=sc,
            ollama_compatible=True,
            airllm_compatible=True,
            description="ok",
        )
        assert e.size_class == sc


# T158 — to_dict / from_dict roundtrip
def test_model_entry_to_dict_from_dict_roundtrip(models_json: Path):
    reg = _registry(models_json)
    entry = reg.get_model("model_a")
    d = entry.to_dict()
    restored = ModelEntry.from_dict(d)
    assert restored.name == entry.name
    assert restored.hf_repo_id == entry.hf_repo_id
    assert restored.size_class == entry.size_class
    assert restored.param_count_b == entry.param_count_b


def test_model_entry_str(models_json: Path):
    reg = _registry(models_json)
    assert str(reg.get_model("model_a")) == "model_a (large)"
    assert str(reg.get_model("model_b")) == "model_b (small)"


def test_model_entry_ollama_tag_for(models_json: Path):
    reg = _registry(models_json)
    tag = reg.get_model("model_a").ollama_tag_for("Q4")
    assert "q4" in tag.lower() or "Q4" in tag


def test_model_entry_airllm_param_for(models_json: Path):
    reg = _registry(models_json)
    param = reg.get_model("model_a").airllm_param_for("Q8")
    assert param == "8bit"


# ── ModelRegistry load_config ─────────────────────────────────────────────────


# T146 — happy path load
def test_load_config_populates_registry(models_json: Path):
    reg = _registry(models_json)
    assert reg.count == 2


# T159 — empty models list raises
def test_load_config_empty_models_raises(tmp_path: Path):
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    reg = ModelRegistry(gk)
    with pytest.raises(RegistryError, match="No models"):
        reg.load_config(str(_empty_json(tmp_path)))


def test_load_config_missing_file_raises(tmp_path: Path):
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    reg = ModelRegistry(gk)
    with pytest.raises(RegistryError, match="Cannot load"):
        reg.load_config(str(tmp_path / "nonexistent.json"))


def test_load_config_invalid_json_raises(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    reg = ModelRegistry(gk)
    with pytest.raises(RegistryError):
        reg.load_config(str(p))


# ── get_model ────────────────────────────────────────────────────────────────


# T147 — get_model returns correct entry
def test_get_model_returns_entry(models_json: Path):
    reg = _registry(models_json)
    entry = reg.get_model("model_a")
    assert isinstance(entry, ModelEntry)
    assert entry.hf_repo_id == "test-org/model-a-7b"


# T148 — get_model raises KeyError for unknown name
def test_get_model_unknown_name_raises(models_json: Path):
    reg = _registry(models_json)
    with pytest.raises(KeyError, match="model_x"):
        reg.get_model("model_x")


# ── list_models / list_names ──────────────────────────────────────────────────


# T151 — list_models returns all entries
def test_list_models_returns_all(models_json: Path):
    reg = _registry(models_json)
    models = reg.list_models()
    assert len(models) == 2
    assert all(isinstance(m, ModelEntry) for m in models)


# T160 — list_names returns sorted list
def test_list_names_returns_sorted(models_json: Path):
    reg = _registry(models_json)
    names = reg.list_names()
    assert names == sorted(names)
    assert "model_a" in names
    assert "model_b" in names


# T152 — count returns correct integer
def test_count_returns_correct_integer(models_json: Path):
    reg = _registry(models_json)
    assert reg.count == 2


# ── filter_by_framework ───────────────────────────────────────────────────────


# T149 — filter by ollama returns only ollama-compatible
def test_filter_by_framework_ollama(models_json: Path):
    reg = _registry(models_json)
    result = reg.filter_by_framework("ollama")
    assert len(result) == 2
    assert all(m.ollama_compatible for m in result)


# T156 — filter by airllm returns only airllm-compatible
def test_filter_by_framework_airllm(models_json: Path):
    reg = _registry(models_json)
    result = reg.filter_by_framework("airllm")
    assert len(result) == 2
    assert all(m.airllm_compatible for m in result)


def test_filter_by_framework_unknown_returns_empty(models_json: Path):
    reg = _registry(models_json)
    assert reg.filter_by_framework("vllm") == []


def test_filter_excludes_incompatible_model(tmp_path: Path):
    data = {
        "models": [
            {
                "name": "a",
                "hf_repo_id": "org/a",
                "ollama_tag": "a:latest",
                "local_cache": str(tmp_path),
                "size_class": "small",
                "param_count_b": 1.0,
                "ollama_compatible": True,
                "airllm_compatible": False,
                "description": "ollama only",
            },
            {
                "name": "b",
                "hf_repo_id": "org/b",
                "ollama_tag": "b:latest",
                "local_cache": str(tmp_path),
                "size_class": "large",
                "param_count_b": 7.0,
                "ollama_compatible": False,
                "airllm_compatible": True,
                "description": "airllm only",
            },
        ]
    }
    p = tmp_path / "mixed.json"
    p.write_text(json.dumps(data))
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    reg = ModelRegistry(gk)
    reg.load_config(str(p))
    assert len(reg.filter_by_framework("ollama")) == 1
    assert reg.filter_by_framework("ollama")[0].name == "a"
    assert len(reg.filter_by_framework("airllm")) == 1
    assert reg.filter_by_framework("airllm")[0].name == "b"


# ── validate / HOOK detection ─────────────────────────────────────────────────


# T150 — HOOK placeholder raises RegistryError
def test_hook_placeholder_raises_registry_error(tmp_path: Path):
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    reg = ModelRegistry(gk)
    with pytest.raises(RegistryError, match="HOOK"):
        reg.load_config(str(_hook_json(tmp_path)))


# T166 — two valid entries work fine
def test_two_valid_entries_load_cleanly(models_json: Path):
    reg = _registry(models_json)
    assert reg.count == 2
    assert reg.get_model("model_a").size_class == "large"
    assert reg.get_model("model_b").size_class == "small"


# ── check_local ───────────────────────────────────────────────────────────────


# T153 — check_local returns False when cache missing
def test_check_local_false_when_missing(models_json: Path):
    reg = _registry(models_json)
    entry = reg.get_model("model_a")
    assert reg.check_local(entry) is False


def test_check_local_true_when_dir_exists_with_content(
    models_json: Path, tmp_path: Path
):
    reg = _registry(models_json)
    entry = reg.get_model("model_a")
    cache = Path(entry.local_cache)
    cache.mkdir(parents=True)
    (cache / "dummy_weight.bin").write_text("data")
    assert reg.check_local(entry) is True


def test_check_local_false_when_dir_empty(models_json: Path):
    reg = _registry(models_json)
    entry = reg.get_model("model_a")
    cache = Path(entry.local_cache)
    cache.mkdir(parents=True)
    assert reg.check_local(entry) is False


# ── ensure_downloaded ─────────────────────────────────────────────────────────


# T154 — ensure_downloaded calls gatekeeper wrapping snapshot_download
def test_ensure_downloaded_calls_gatekeeper(models_json: Path):
    gk = MagicMock(spec=ApiGatekeeper)
    gk.execute.side_effect = lambda fn, **kw: fn(**kw)
    reg = ModelRegistry(gk)
    reg.load_config(str(models_json))
    entry = reg.get_model("model_a")

    with (
        patch("hw5.services.model_registry.snapshot_download"),
        patch.object(reg, "check_local", return_value=False),
    ):
        reg.ensure_downloaded(entry)

    gk.execute.assert_called_once()


def test_ensure_downloaded_skips_when_already_cached(models_json: Path):
    gk = MagicMock(spec=ApiGatekeeper)
    reg = ModelRegistry(gk)
    reg.load_config(str(models_json))
    entry = reg.get_model("model_a")

    with patch.object(reg, "check_local", return_value=True):
        reg.ensure_downloaded(entry)

    gk.execute.assert_not_called()


def test_ensure_downloaded_dry_run_does_not_call_gatekeeper(models_json: Path):
    gk = MagicMock(spec=ApiGatekeeper)
    reg = ModelRegistry(gk)
    reg.load_config(str(models_json))
    entry = reg.get_model("model_b")

    reg.ensure_downloaded(entry, dry_run=True)
    gk.execute.assert_not_called()


# T155 — ensure_downloaded raises DownloadError on failure
def test_ensure_downloaded_raises_download_error_on_failure(models_json: Path):
    gk = ApiGatekeeper(rate=1000.0, burst=10)
    gk.execute = MagicMock(side_effect=RuntimeError("network error"))  # type: ignore
    reg = ModelRegistry(gk)
    reg.load_config(str(models_json))
    entry = reg.get_model("model_a")

    with patch.object(reg, "check_local", return_value=False):
        with pytest.raises(DownloadError, match="network error"):
            reg.ensure_downloaded(entry)
