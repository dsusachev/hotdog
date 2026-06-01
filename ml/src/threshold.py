"""Threshold tuning for unknown-detection (task #44).

Definitions (ml_aproach.md §9, §8):
  coverage(t)            = fraction of inputs with max_prob >= t
  selective_accuracy(t)  = accuracy on covered inputs only
  rejected(t)            = fraction of inputs flagged as unknown (= 1 - coverage)

Selection rule chosen for the MVP: take the largest threshold whose
selective_accuracy on the validation set is >= MIN_SELECTIVE_ACCURACY.
That is the standard selective-prediction trade-off: among all thresholds
that meet a target accuracy on "confident" inputs, pick the one that
covers the most input.
"""
from __future__ import annotations

import numpy as np

DEFAULT_GRID = np.round(np.arange(0.0, 1.001, 0.01), 4)
MIN_SELECTIVE_ACCURACY = 0.95


def compute_threshold_curve(
    logits: np.ndarray,
    labels: np.ndarray,
    grid: np.ndarray = DEFAULT_GRID,
) -> list[dict]:
    """For each threshold on the grid compute coverage and selective accuracy.

    `logits` and `labels` come from evaluate.predict_all on the chosen split.
    """
    probs = _softmax(logits)
    max_probs = probs.max(axis=1)
    preds = probs.argmax(axis=1)
    correct = (preds == labels)
    n = len(labels)

    out: list[dict] = []
    for t in grid:
        covered = max_probs >= t
        n_covered = int(covered.sum())
        coverage = n_covered / n
        if n_covered == 0:
            sel_acc = float("nan")
        else:
            sel_acc = float(correct[covered].mean())
        out.append({
            "threshold": float(t),
            "coverage": float(coverage),
            "selective_accuracy": sel_acc,
            "n_covered": n_covered,
            "n_correct_in_covered": int(correct[covered].sum()),
            "n_rejected": n - n_covered,
        })
    return out


def recommend_threshold(
    curve: list[dict],
    min_selective_accuracy: float = MIN_SELECTIVE_ACCURACY,
) -> dict:
    """Return the row from `curve` with max coverage at sel_acc >= target.

    If no threshold meets the target, returns the row with the highest
    selective_accuracy (best effort), and marks `target_met=False`.
    """
    eligible = [
        r for r in curve
        if not np.isnan(r["selective_accuracy"])
        and r["selective_accuracy"] >= min_selective_accuracy
    ]
    if eligible:
        # max coverage; tie-break by higher selective_accuracy.
        winner = max(
            eligible,
            key=lambda r: (r["coverage"], r["selective_accuracy"]),
        )
        return {
            **winner,
            "target_selective_accuracy": min_selective_accuracy,
            "target_met": True,
        }
    # Fallback: best sel_acc we can get.
    fallback = max(
        (r for r in curve if not np.isnan(r["selective_accuracy"])),
        key=lambda r: r["selective_accuracy"],
    )
    return {
        **fallback,
        "target_selective_accuracy": min_selective_accuracy,
        "target_met": False,
    }


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=1, keepdims=True)
