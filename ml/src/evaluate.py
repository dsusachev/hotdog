from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from torch.utils.data import DataLoader

from src.dataset import NUM_COARSE_CLASSES


def load_class_names(dataset_root: str | Path) -> list[str]:
    """Read coarse class names from classes.csv, ordered by coarse_id 0..42."""
    path = Path(dataset_root) / "classes.csv"
    coarse: dict[int, str] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = int(row["Coarse Class ID (int)"])
            cname = row["Coarse Class Name (str)"]
            coarse[cid] = cname
    return [coarse[i] for i in range(NUM_COARSE_CLASSES)]


@torch.no_grad()
def predict_all(
    model: nn.Module, loader: DataLoader, device: torch.device
) -> tuple[np.ndarray, np.ndarray]:
    """Run model on the whole loader, return (logits, labels) as numpy arrays."""
    model.eval()
    all_logits = []
    all_labels = []
    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        logits = model(images)
        all_logits.append(logits.detach().cpu().numpy())
        all_labels.append(labels.numpy())
    return np.concatenate(all_logits), np.concatenate(all_labels)


def _topk_accuracy(logits: np.ndarray, labels: np.ndarray, k: int) -> float:
    topk = np.argpartition(-logits, kth=k - 1, axis=1)[:, :k]
    hit = (topk == labels[:, None]).any(axis=1)
    return float(hit.mean())


def compute_metrics(
    logits: np.ndarray,
    labels: np.ndarray,
    class_names: list[str],
) -> dict:
    """Compute top-1/top-3/macro-F1/per-class metrics and confusion matrix."""
    preds = logits.argmax(axis=1)
    n_classes = len(class_names)
    labels_arr = np.asarray(labels)

    classes_present = sorted(set(int(c) for c in np.unique(labels_arr)))
    classes_missing = [i for i in range(n_classes) if i not in set(classes_present)]

    top1 = _topk_accuracy(logits, labels_arr, k=1)
    top3 = _topk_accuracy(logits, labels_arr, k=3)

    macro_f1 = f1_score(
        labels_arr,
        preds,
        labels=list(range(n_classes)),
        average="macro",
        zero_division=0,
    )
    weighted_f1 = f1_score(
        labels_arr,
        preds,
        labels=list(range(n_classes)),
        average="weighted",
        zero_division=0,
    )
    # Honest macro_f1 across only classes actually present in this split:
    macro_f1_present = f1_score(
        labels_arr,
        preds,
        labels=classes_present,
        average="macro",
        zero_division=0,
    )

    precision, recall, f1, support = precision_recall_fscore_support(
        labels_arr,
        preds,
        labels=list(range(n_classes)),
        zero_division=0,
    )
    per_class = []
    for i in range(n_classes):
        per_class.append(
            {
                "class_id": i,
                "class_name": class_names[i],
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
        )

    cm = confusion_matrix(labels_arr, preds, labels=list(range(n_classes)))

    report = classification_report(
        labels_arr,
        preds,
        labels=list(range(n_classes)),
        target_names=class_names,
        zero_division=0,
        digits=3,
    )

    return {
        "top1": top1,
        "top3": top3,
        "macro_f1_all_classes": float(macro_f1),
        "macro_f1_present_only": float(macro_f1_present),
        "weighted_f1": float(weighted_f1),
        "n_samples": int(len(labels_arr)),
        "n_classes_total": n_classes,
        "n_classes_present": len(classes_present),
        "classes_missing_ids": classes_missing,
        "classes_missing_names": [class_names[i] for i in classes_missing],
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "classification_report_text": report,
    }


def save_metrics(metrics: dict, out_path: Path) -> None:
    out_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))


def save_per_class_csv(metrics: dict, out_path: Path) -> None:
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "class_id",
                "class_name",
                "precision",
                "recall",
                "f1",
                "support",
            ],
        )
        writer.writeheader()
        for row in metrics["per_class"]:
            writer.writerow(row)


def plot_confusion_matrix(
    metrics: dict, class_names: list[str], out_path: Path, normalize: bool = True
) -> None:
    """Save a confusion-matrix heatmap. Lazy-imports matplotlib/seaborn."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    cm = np.array(metrics["confusion_matrix"], dtype=np.float64)
    if normalize:
        row_sum = cm.sum(axis=1, keepdims=True)
        cm = np.divide(cm, row_sum, out=np.zeros_like(cm), where=row_sum > 0)

    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(
        cm,
        xticklabels=class_names,
        yticklabels=class_names,
        cmap="Blues",
        vmin=0,
        vmax=1 if normalize else None,
        cbar_kws={"label": "row-normalized" if normalize else "count"},
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    title = f"Confusion matrix (top-1={metrics['top1']:.3f}, n={metrics['n_samples']})"
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
    plt.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
