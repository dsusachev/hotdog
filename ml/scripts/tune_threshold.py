"""Tune softmax threshold on validation set (task #44).

Usage:
    python ml/scripts/tune_threshold.py \
        --artifact ml/artifacts/resnet50_v1_20260519.pt

Steps:
  1. Run the model on the validation split, save max_prob + correctness.
  2. Build a coverage-vs-selective-accuracy curve on a 0.00..1.00 grid.
  3. Pick the largest threshold whose selective_accuracy >= 0.95.
  4. Write next to the artifact:
       <stem>_threshold_curve.csv
       <stem>_threshold_curve.png
       <stem>_threshold.json (chosen value + decision context)
  5. Update artifact.threshold in-place (unless --no-update).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.artifact import (  # noqa: E402
    build_eval_transform_from_artifact,
    build_model_from_artifact,
    load_artifact,
    save_artifact,
)
from src.dataset import GroceryStoreDataset  # noqa: E402
from src.evaluate import predict_all  # noqa: E402
from src.threshold import (  # noqa: E402
    MIN_SELECTIVE_ACCURACY,
    compute_threshold_curve,
    recommend_threshold,
)
from src.train import pick_device  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

DEFAULT_DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", type=Path, required=True)
    p.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    p.add_argument("--split", default="val", choices=["val", "test"],
                   help="ml_aproach.md mandates val; --split test is for inspection only")
    p.add_argument("--target-selective-accuracy", type=float,
                   default=MIN_SELECTIVE_ACCURACY)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--no-update", action="store_true",
                   help="Don't write threshold back into the artifact")
    return p.parse_args()


def _plot_curve(curve, chosen, out_path: Path) -> None:
    import matplotlib.pyplot as plt
    thresholds = [r["threshold"] for r in curve]
    coverage = [r["coverage"] for r in curve]
    sel_acc = [r["selective_accuracy"] for r in curve]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()
    ax1.plot(thresholds, coverage, label="coverage", color="#1f77b4")
    ax2.plot(thresholds, sel_acc, label="selective accuracy", color="#d62728")
    ax1.set_xlabel("threshold")
    ax1.set_ylabel("coverage", color="#1f77b4")
    ax2.set_ylabel("selective accuracy", color="#d62728")
    ax1.set_ylim(0, 1.05)
    ax2.set_ylim(0, 1.05)
    ax1.axvline(chosen["threshold"], linestyle="--", color="gray", alpha=0.6)
    ax1.set_title(
        f"chosen threshold={chosen['threshold']:.2f}  "
        f"(coverage={chosen['coverage']:.3f}, "
        f"sel_acc={chosen['selective_accuracy']:.3f})"
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    artifact = load_artifact(args.artifact)
    print(f"Artifact: {args.artifact.name}, model_version={artifact['model_version']}")

    device = pick_device()
    model = build_model_from_artifact(artifact).to(device).eval()
    transform = build_eval_transform_from_artifact(artifact)

    ds = GroceryStoreDataset(args.dataset_root, args.split, transform=transform)
    loader = DataLoader(
        ds, batch_size=args.batch_size, shuffle=False,
        num_workers=0, pin_memory=(device.type == "cuda"),
    )
    logits, labels = predict_all(model, loader, device)
    print(f"Predicted {len(labels)} {args.split} samples")

    curve = compute_threshold_curve(logits, labels)
    chosen = recommend_threshold(curve, args.target_selective_accuracy)
    print(f"\nTarget selective_accuracy >= {args.target_selective_accuracy}")
    print(f"  chosen threshold:        {chosen['threshold']:.2f}")
    print(f"  selective_accuracy:      {chosen['selective_accuracy']:.4f}")
    print(f"  coverage:                {chosen['coverage']:.4f} "
          f"({chosen['n_covered']}/{chosen['n_covered']+chosen['n_rejected']})")
    print(f"  target met:              {chosen['target_met']}")

    print("\nCurve (sampled every 0.05):")
    for r in curve[::5]:
        print(f"  t={r['threshold']:.2f}  cov={r['coverage']:.3f}  "
              f"sel_acc={r['selective_accuracy']:.3f}  n_cov={r['n_covered']}")

    stem = args.artifact.with_suffix("")
    csv_path = stem.with_name(stem.name + "_threshold_curve.csv")
    png_path = stem.with_name(stem.name + "_threshold_curve.png")
    json_path = stem.with_name(stem.name + "_threshold.json")

    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(curve[0].keys()))
        w.writeheader()
        for r in curve:
            w.writerow(r)
    _plot_curve(curve, chosen, png_path)
    json_path.write_text(json.dumps({
        "split_used": args.split,
        "n_samples": len(labels),
        "target_selective_accuracy": args.target_selective_accuracy,
        "chosen": chosen,
    }, indent=2))

    print(f"\nSaved: {csv_path.name}, {png_path.name}, {json_path.name}")

    if args.no_update:
        print("\n--no-update set; artifact threshold left unchanged")
        return

    artifact["threshold"] = float(chosen["threshold"])
    save_artifact(artifact, args.artifact)
    print(f"\nUpdated {args.artifact.name}: threshold = {artifact['threshold']:.2f}")


if __name__ == "__main__":
    main()
