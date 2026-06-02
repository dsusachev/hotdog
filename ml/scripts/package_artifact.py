"""Package a trained run into a single production artifact (task #40).

Usage:
    python ml/scripts/package_artifact.py \
        --run-dir ml/runs/20260518_104246_resnet50 \
        --version-tag v1

Reads best.pt + config.json + eval_summary.json + classes.csv from the run,
writes ml/artifacts/<backbone>_<tag>_<YYYYMMDD>.pt with full metadata.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.artifact import build_artifact_dict, save_artifact  # noqa: E402
from src.evaluate import load_class_names  # noqa: E402

DEFAULT_DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"
DEFAULT_ARTIFACTS_ROOT = REPO_ROOT / "ml" / "artifacts"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--checkpoint", default="best.pt", choices=["best.pt", "last.pt"])
    p.add_argument("--version-tag", default="v1")
    p.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    p.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS_ROOT)
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Explicit output path. Overrides version-tag/artifacts-root.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir.resolve()

    ckpt = torch.load(run_dir / args.checkpoint, map_location="cpu", weights_only=False)
    config = json.loads((run_dir / "config.json").read_text())
    eval_summary_path = run_dir / "eval_summary.json"
    if not eval_summary_path.exists():
        raise FileNotFoundError(
            f"{eval_summary_path} not found — run evaluate_model.py first"
        )
    eval_summary = json.loads(eval_summary_path.read_text())

    backbone = config["backbone"]
    num_classes = config["num_classes"]
    class_names = load_class_names(args.dataset_root)
    if len(class_names) != num_classes:
        raise ValueError(
            f"classes.csv has {len(class_names)} classes but config has {num_classes}"
        )

    metrics = {
        "val": eval_summary.get("val"),
        "test": eval_summary.get("test"),
    }

    model_version = f"{backbone}_{args.version_tag}_{datetime.now():%Y%m%d}"

    artifact = build_artifact_dict(
        model_state=ckpt["model_state"],
        backbone=backbone,
        num_classes=num_classes,
        class_names=class_names,
        metrics=metrics,
        train_config=config,
        source_run_dir=run_dir,
        model_version=model_version,
    )

    if args.out is not None:
        out_path = args.out
    else:
        out_path = args.artifacts_root / f"{model_version}.pt"

    saved = save_artifact(artifact, out_path)
    size_mb = saved.stat().st_size / 1e6
    print(f"Saved artifact: {saved} ({size_mb:.1f} MB)")
    print(f"  model_version: {model_version}")
    print(f"  backbone:      {backbone}")
    print(f"  num_classes:   {num_classes}")
    print(f"  metrics.test.top1: {metrics['test']['top1']:.4f}")


if __name__ == "__main__":
    main()
