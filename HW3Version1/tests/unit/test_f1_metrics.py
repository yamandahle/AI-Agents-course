"""Unit tests for F1 metrics computation (eval/f1_metrics.py)."""
import pytest

from article_writer.eval.f1_metrics import compute_f1, format_report, F1Result


def test_perfect_predictions():
    preds = ["PASS", "FAIL", "PASS"]
    labels = ["PASS", "FAIL", "PASS"]
    result = compute_f1(preds, labels)
    assert result.f1 == 1.0
    assert result.precision == 1.0
    assert result.recall == 1.0


def test_all_wrong_predictions():
    preds = ["PASS", "PASS"]
    labels = ["FAIL", "FAIL"]
    result = compute_f1(preds, labels)
    assert result.precision == 0.0
    assert result.f1 == 0.0


def test_all_fn():
    preds = ["FAIL", "FAIL"]
    labels = ["PASS", "PASS"]
    result = compute_f1(preds, labels)
    assert result.recall == 0.0
    assert result.f1 == 0.0


def test_mixed_predictions():
    preds =  ["PASS", "FAIL", "PASS", "FAIL"]
    labels = ["PASS", "FAIL", "FAIL", "PASS"]
    result = compute_f1(preds, labels)
    assert result.tp == 1
    assert result.fp == 1
    assert result.fn == 1
    assert result.tn == 1


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        compute_f1(["PASS"], ["PASS", "FAIL"])


def test_f1_formula_correctness():
    preds  = ["PASS", "PASS", "PASS", "FAIL"]
    labels = ["PASS", "PASS", "FAIL", "FAIL"]
    result = compute_f1(preds, labels)
    expected_p = 2 / 3
    expected_r = 1.0
    expected_f1 = 2 * expected_p * expected_r / (expected_p + expected_r)
    assert abs(result.f1 - expected_f1) < 1e-4


def test_format_report_contains_f1():
    r = F1Result(precision=0.8, recall=0.75, f1=0.774, tp=3, fp=0, fn=1, tn=1, accuracy=0.9)
    report = format_report(r, "dev")
    assert "F1" in report
    assert "0.774" in report
    assert "dev" in report


def test_case_insensitive_positive_class():
    preds  = ["pass", "fail"]
    labels = ["PASS", "FAIL"]
    result = compute_f1(preds, labels, positive_class="PASS")
    assert result.tp == 1
