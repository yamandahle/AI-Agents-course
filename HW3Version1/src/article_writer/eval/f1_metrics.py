"""F1 metric computation for LLM judge evaluation against human labels."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class F1Result:
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int
    tn: int
    accuracy: float


def compute_f1(
    predictions: list[str],
    ground_truth: list[str],
    positive_class: str = "PASS",
) -> F1Result:
    """Compute binary F1 between judge predictions and human labels."""
    if len(predictions) != len(ground_truth):
        raise ValueError("predictions and ground_truth must have the same length")

    tp = fp = fn = tn = 0
    for pred, gt in zip(predictions, ground_truth):
        p_pos = pred.upper() == positive_class.upper()
        g_pos = gt.upper() == positive_class.upper()
        if p_pos and g_pos:
            tp += 1
        elif p_pos and not g_pos:
            fp += 1
        elif not p_pos and g_pos:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0.0

    return F1Result(
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        tp=tp, fp=fp, fn=fn, tn=tn,
        accuracy=round(accuracy, 4),
    )


def format_report(result: F1Result, split_name: str = "dev") -> str:
    return (
        f"=== F1 Report ({split_name}) ===\n"
        f"Precision : {result.precision:.4f}\n"
        f"Recall    : {result.recall:.4f}\n"
        f"F1        : {result.f1:.4f}\n"
        f"Accuracy  : {result.accuracy:.4f}\n"
        f"TP={result.tp} FP={result.fp} FN={result.fn} TN={result.tn}"
    )
