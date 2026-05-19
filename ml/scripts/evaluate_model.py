"""Evaluate a trained checkpoint on val + test splits (task #39).

Usage:
    python ml/scripts/evaluate_model.py --run-dir ml/runs/20260518_104246_resnet50

Writes inside the run-dir:
    eval_<split>.json              — full metrics dict
    eval_<split>_per_class.csv     — per-class precision/recall/f1/support
    eval_<split>_confusion.png     — row-normalized confusion matrix
    eval_summary.json              — compact summary (top-1/top-3/macro_f1, val+test)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.dataset import GroceryStoreDataset  # noqa: E402
from src.evaluate import (  # noqa: E402
    compute_metrics,
    load_class_names,
    plot_confusion_matrix,
    predict_all,
    save_metrics,
    save_per_class_csv,
)
from src.model import build_model  # noqa: E402
from src.train import pick_device  # noqa: E402
from src.transforms import build_eval_transform  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

DEFAULT_DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, required=True,
                   help="Run directory created by run_training.py")
    p.add_argument("--checkpoint", type=str, default="best.pt",
                   choices=["best.pt", "last.pt"])
    p.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--num-workers", type=int, default=2)
    p.add_argument("--splits", type=str, default="val,test")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    ckpt_path = run_dir / args.checkpoint
    config_path = run_dir / "config.json"
    if not ckpt_path.exists():
        raise FileNotFoundError(ckpt_path)
    if not config_path.exists():
        raise FileNotFoundError(config_path)

    config = json.loads(config_path.read_text())
    backbone = config["backbone"]
    num_classes = config["num_classes"]
    print(f"Run: {run_dir.name}")
    print(f"Backbone: {backbone}, num_classes: {num_classes}, ckpt: {args.checkpoint}")

    device = pick_device()
    print(f"Device: {device}")
    model = build_model(backbone, num_classes=num_classes, pretrained=False)
    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model.load_state_dict(state["model_state"])
    model.to(device)
    model.eval()

    class_names = load_class_names(args.dataset_root)
    eval_transform = build_eval_transform()

    summary = {"run_dir": str(run_dir), "checkpoint": args.checkpoint, "backbone": backbone}
    for split in args.splits.split(","):
        split = split.strip()
        print(f"\n=== Evaluating on {split} ===")
        ds = GroceryStoreDataset(args.dataset_root, split, transform=eval_transform)
        loader = DataLoader(
            ds, batch_size=args.batch_size, shuffle=False,
            num_workers=args.num_workers, pin_memory=(device.type == "cuda"),
        )
        logits, labels = predict_all(model, loader, device)
        metrics = compute_metrics(logits, labels, class_names)

        save_metrics(metrics, run_dir / f"eval_{split}.json")
        save_per_class_csv(metrics, run_dir / f"eval_{split}_per_class.csv")
        plot_confusion_matrix(metrics, class_names, run_dir / f"eval_{split}_confusion.png")

        print(f"top1={metrics['top1']:.4f}, top3={metrics['top3']:.4f}, "
              f"macro_f1={metrics['macro_f1_all_classes']:.4f} "
              f"(present_only={metrics['macro_f1_present_only']:.4f}), "
              f"n={metrics['n_samples']}, "
              f"classes_present={metrics['n_classes_present']}/{metrics['n_classes_total']}")
        if metrics["classes_missing_names"]:
            print(f"classes missing in {split}: {metrics['classes_missing_names']}")

        summary[split] = {
            "top1": metrics["top1"],
            "top3": metrics["top3"],
            "macro_f1_all_classes": metrics["macro_f1_all_classes"],
            "macro_f1_present_only": metrics["macro_f1_present_only"],
            "weighted_f1": metrics["weighted_f1"],
            "n_samples": metrics["n_samples"],
            "n_classes_present": metrics["n_classes_present"],
        }

    (run_dir / "eval_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    print(f"\nSaved: eval_*.json, eval_*_per_class.csv, eval_*_confusion.png in {run_dir}")


if __name__ == "__main__":
    main()
