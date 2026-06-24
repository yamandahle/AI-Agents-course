"""T169: Integration test for ModelRegistry.ensure_downloaded.

Requires HF_TOKEN environment variable to be set.
Run with: INTEGRATION=1 pytest tests/integration/ -m integration
"""

from __future__ import annotations

import os

import pytest

from hw5.services.model_registry import ModelRegistry
from hw5.shared.gatekeeper import ApiGatekeeper

_HF_TOKEN = os.getenv("HF_TOKEN", "")


@pytest.mark.integration
@pytest.mark.skipif(
    not _HF_TOKEN, reason="HF_TOKEN not set — skipping HuggingFace download test"
)
def test_ensure_downloaded_fetches_small_public_model(tmp_path):
    """Download a tiny public model to verify end-to-end HF integration."""
    import json

    models_data = {
        "models": [
            {
                "name": "tiny_test",
                "hf_repo_id": "hf-internal-testing/tiny-random-gpt2",
                "ollama_tag": "gpt2:tiny",
                "local_cache": str(tmp_path / "hf_cache"),
                "size_class": "small",
                "param_count_b": 0.001,
                "ollama_compatible": False,
                "airllm_compatible": True,
                "description": "Tiny public model for integration testing",
                "quant_ollama_tags": {},
                "quant_airllm_params": {"Q4": "4bit"},
            }
        ]
    }
    cfg_path = tmp_path / "models.json"
    cfg_path.write_text(json.dumps(models_data))

    gk = ApiGatekeeper(rate=5.0, burst=3)
    reg = ModelRegistry(gk)
    reg.load_config(str(cfg_path))

    entry = reg.get_model("tiny_test")
    assert not reg.check_local(entry), "Cache should be empty before download"

    reg.ensure_downloaded(entry)
    assert reg.check_local(entry), "Cache should be populated after download"
