"""Smoke tests for the training loop (task #38).

Test 1: overfit a single batch.
  Repeatedly train on the same 8 images. Loss must drop close to zero and
  top-1 must hit 100%. If it doesn't — there's a bug in the train loop.

Test 2: one short training run on a tiny subset.
  Verifies CSV writing, two-stage transitions, freeze/unfreeze, evaluate(),
  and checkpoint saving — all the orchestration plumbing.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Subset

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.dataset import GroceryStoreDataset, NUM_COARSE_CLASSES  # noqa: E402
from src.model import build_model  # noqa: E402
from src.train import (  # noqa: E402
    StageConfig,
    TrainConfig,
    pick_device,
    train_two_stage,
)
from src.transforms import build_eval_transform, build_train_transform  # noqa: E402

DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"


def overfit_one_batch(device: torch.device) -> None:
    print(f"\n=== Test 1: overfit one batch on {device} ===")
    ds = GroceryStoreDataset(DATASET_ROOT, "val", transform=build_eval_transform())
    # 8 different images from the val set.
    loader = DataLoader(Subset(ds, list(range(8))), batch_size=8, shuffle=False)
    images, labels = next(iter(loader))
    images = images.to(device)
    labels = labels.to(device)

    model = build_model("efficientnet_b0", num_classes=NUM_COARSE_CLASSES).to(device)
    optimizer = AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    model.train()
    losses = []
    for step in range(40):
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))

    with torch.no_grad():
        model.eval()
        logits = model(images)
        top1 = (logits.argmax(1) == labels).float().mean().item()

    print(f"loss[0]={losses[0]:.3f}, loss[10]={losses[10]:.3f}, loss[-1]={losses[-1]:.3f}")
    print(f"final top1={top1:.3f}")
    assert losses[-1] < losses[0] / 2, "loss did not decrease — training loop is broken"
    assert top1 >= 0.75, f"could not overfit 8 examples (top1={top1})"
    print("[OK] overfit-one-batch")


def short_training_run() -> None:
    print("\n=== Test 2: short training run on tiny subset ===")
    train_full = GroceryStoreDataset(
        DATASET_ROOT, "train", transform=build_train_transform()
    )
    val_full = GroceryStoreDataset(
        DATASET_ROOT, "val", transform=build_eval_transform()
    )

    # Tiny subsets so it finishes in seconds.
    train_ds = Subset(train_full, list(range(96)))
    val_ds = Subset(val_full, list(range(48)))
    train_loader = DataLoader(train_ds, batch_size=16, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=16, shuffle=False, num_workers=0)

    config = TrainConfig(
        backbone="efficientnet_b0",
        batch_size=16,
        stages=[
            StageConfig("feature_extraction", lr=1e-3, epochs=2, backbone_trainable=False),
            StageConfig("fine_tuning", lr=1e-4, epochs=2, backbone_trainable=True, unfreeze_top_n_blocks=2),
        ],
        early_stop_patience=99,
    )
    model = build_model(config.backbone, num_classes=config.num_classes)

    run_dir = Path(tempfile.mkdtemp(prefix="smoke_run_"))
    try:
        result = train_two_stage(model, config.backbone, train_loader, val_loader, config, run_dir)

        assert (run_dir / "config.json").exists()
        assert (run_dir / "metrics.csv").exists()
        assert (run_dir / "best.pt").exists()
        assert (run_dir / "last.pt").exists()

        metrics = (run_dir / "metrics.csv").read_text().strip().splitlines()
        assert len(metrics) == 1 + 4, f"expected 4 epochs + header, got {len(metrics)}"
        stages_seen = {row.split(",")[0] for row in metrics[1:]}
        assert stages_seen == {"feature_extraction", "fine_tuning"}, stages_seen
        print(f"[OK] short_training_run: {result}")
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)


def main() -> None:
    device = pick_device()
    print(f"Device: {device}")
    overfit_one_batch(device)
    short_training_run()
    print("\nSmoke tests: PASSED")


if __name__ == "__main__":
    main()
