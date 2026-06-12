"""Unit tests for Tracer (shared/tracer.py)."""
import json
import tempfile
from pathlib import Path

import pytest

from article_writer.shared.tracer import Tracer


@pytest.fixture
def tmp_tracer(tmp_path):
    return Tracer(path=tmp_path / "traces.jsonl")


def test_log_writes_one_record(tmp_tracer, tmp_path):
    tmp_tracer.log(step="test_step", model="gpt-4", provider="openai",
                   input="hello", output="world", input_tokens=5, output_tokens=3)
    records = tmp_tracer.read_all()
    assert len(records) == 1
    assert records[0]["step"] == "test_step"
    assert records[0]["model"] == "gpt-4"


def test_log_multiple_calls_appends(tmp_tracer):
    tmp_tracer.log(step="step1", model="m1", provider="p1")
    tmp_tracer.log(step="step2", model="m2", provider="p2")
    records = tmp_tracer.read_all()
    assert len(records) == 2


def test_log_truncates_long_input(tmp_tracer):
    long_text = "x" * 10000
    tmp_tracer.log(step="s", model="m", provider="p", input=long_text)
    records = tmp_tracer.read_all()
    assert len(records[0]["input"]) <= 6000


def test_log_truncates_long_output(tmp_tracer):
    long_text = "y" * 10000
    tmp_tracer.log(step="s", model="m", provider="p", output=long_text)
    records = tmp_tracer.read_all()
    assert len(records[0]["output"]) <= 6000


def test_log_tool_sets_tool_name(tmp_tracer):
    tmp_tracer.log_tool(tool_name="deep_research", input_data={"q": "test"}, output_data="result")
    records = tmp_tracer.read_all()
    assert records[0]["tool_name"] == "deep_research"


def test_read_all_empty_when_no_file(tmp_path):
    tracer = Tracer(path=tmp_path / "nonexistent.jsonl")
    assert tracer.read_all() == []


def test_log_includes_timestamp(tmp_tracer):
    tmp_tracer.log(step="s", model="m", provider="p")
    records = tmp_tracer.read_all()
    assert "ts" in records[0]
    assert "T" in records[0]["ts"]


def test_log_metadata_stored(tmp_tracer):
    tmp_tracer.log(step="s", model="m", provider="p", metadata={"key": "value"})
    records = tmp_tracer.read_all()
    assert records[0]["metadata"] == {"key": "value"}


def test_records_are_valid_json(tmp_tracer):
    tmp_tracer.log(step="s", model="m", provider="p", input='{"nested": "json"}')
    path = tmp_tracer._path
    with path.open() as fh:
        line = fh.readline()
    parsed = json.loads(line)
    assert isinstance(parsed, dict)
