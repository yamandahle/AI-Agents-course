"""Unit tests for MetricsTracker (shared/metrics_tracker.py)."""
import json
from pathlib import Path

import pytest

from article_writer.shared.metrics_tracker import MetricsTracker


@pytest.fixture
def tmp_metrics(tmp_path):
    return MetricsTracker(path=tmp_path / "metrics.jsonl")


def test_log_writes_one_record(tmp_metrics):
    tmp_metrics.log(step="draft_v1", model="claude", latency_ms=1500,
                    input_tokens=1000, output_tokens=500, cost_usd=0.005)
    path = tmp_metrics._path
    with path.open() as fh:
        line = fh.readline()
    record = json.loads(line)
    assert record["step"] == "draft_v1"
    assert record["latency_ms"] == 1500


def test_log_computes_total_tokens(tmp_metrics):
    tmp_metrics.log(step="s", model="m", latency_ms=100,
                    input_tokens=400, output_tokens=100, cost_usd=0.001)
    path = tmp_metrics._path
    with path.open() as fh:
        record = json.loads(fh.readline())
    assert record["total_tokens"] == 500


def test_log_rounds_cost(tmp_metrics):
    tmp_metrics.log(step="s", model="m", latency_ms=0,
                    input_tokens=0, output_tokens=0, cost_usd=0.12345678)
    path = tmp_metrics._path
    with path.open() as fh:
        record = json.loads(fh.readline())
    assert record["cost_usd"] == round(0.12345678, 6)


def test_summary_returns_zeros_when_no_file(tmp_path):
    m = MetricsTracker(path=tmp_path / "missing.jsonl")
    result = m.summary()
    assert result["steps"] == 0
    assert result["total_tokens"] == 0
    assert result["total_cost_usd"] == 0.0


def test_summary_aggregates_multiple_records(tmp_metrics):
    tmp_metrics.log(step="s1", model="m", latency_ms=100,
                    input_tokens=100, output_tokens=50, cost_usd=0.001)
    tmp_metrics.log(step="s2", model="m", latency_ms=200,
                    input_tokens=200, output_tokens=100, cost_usd=0.002)
    s = tmp_metrics.summary()
    assert s["steps"] == 2
    assert s["total_tokens"] == 450
    assert abs(s["total_cost_usd"] - 0.003) < 1e-6
    assert s["total_latency_ms"] == 300


def test_log_multiple_records_appended(tmp_metrics):
    for i in range(5):
        tmp_metrics.log(step=f"s{i}", model="m", latency_ms=i,
                        input_tokens=i, output_tokens=i, cost_usd=0.0)
    assert tmp_metrics.summary()["steps"] == 5
