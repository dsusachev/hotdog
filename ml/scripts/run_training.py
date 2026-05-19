"""CLI entry point for training (task #38).

Examples:
    python ml/scripts/run_training.py --backbone efficientnet_b0
    python ml/scripts/run_training.py --backbone resnet50 --run-name resnet50_baseline
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.dataset import NUM_COARSE_CLASSES, build_dataloaders  # noqa: E402
from src.model import build_model  # noqa: E402
from src.train import TrainConfig, train_two_stage  # noqa: E402
from src.transforms import build_eval_transform, build_train_transform  # noqa: E402

DEFAULT_DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"
DEFAULT_RUNS_ROOT = REPO_ROOT / "ml" / "runs"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--backbone", choices=["efficientnet_b0", "resnet50"], required=True)
    p.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    p.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    p.add_argument("--run-name", type=str, default=None,
                   help="If omitted, uses <timestamp>_<backbone>")
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--stage1-epochs", type=int, default=4)
    p.add_argument("--stage2-epochs", type=int, default=15)

    p.add_argument("--stage2-unfreeze-blocks", type=int, default=2,
                   help="How many top backbone blocks to unfreeze on stage 2. "
                        "Use a large number (e.g. 99) to unfreeze the whole backbone.")
    p.add_argument("--stage2-lr", type=float, default=1e-4)

    p.add_argument("--early-stop-patience", type=int, default=6)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    run_name = args.run_name or (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{args.backbone}"
    )
    run_dir = args.runs_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run dir: {run_dir}")

    loaders = build_dataloaders(
        args.dataset_root,
        train_transform=build_train_transform(),
        eval_transform=build_eval_transform(),
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    config = TrainConfig(
        backbone=args.backbone,
        num_classes=NUM_COARSE_CLASSES,
        batch_size=args.batch_size,
        early_stop_patience=args.early_stop_patience,
        seed=args.seed,
    )
    config.stages[0].epochs = args.stage1_epochs
    config.stages[1].epochs = args.stage2_epochs

    config.stages[1].unfreeze_top_n_blocks = args.stage2_unfreeze_blocks
    config.stages[1].lr = args.stage2_lr


    model = build_model(config.backbone, num_classes=config.num_classes)
    result = train_two_stage(
        model, config.backbone, loaders["train"], loaders["val"], config, run_dir
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
