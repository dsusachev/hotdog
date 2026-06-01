"""Sanity-check for preprocessing/augmentations (task #35).

Verifies:
  - eval transform is deterministic (two calls identical)
  - train transform is stochastic (two calls differ)
  - output shape is (3, 224, 224), float32
  - Normalize was applied: mean per channel close to dataset stats, NOT to [0,1]
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.dataset import GroceryStoreDataset  # noqa: E402
from src.transforms import (  # noqa: E402
    INPUT_SIZE,
    build_eval_transform,
    build_train_transform,
)

DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"


def main() -> None:
    raw_ds = GroceryStoreDataset(DATASET_ROOT, "val", transform=None)
    pil_image, _ = raw_ds[0]
    print(f"raw image size (W,H): {pil_image.size}, mode={pil_image.mode}")

    eval_t = build_eval_transform()
    train_t = build_train_transform()

    e1 = eval_t(pil_image)
    e2 = eval_t(pil_image)
    assert e1.shape == (3, INPUT_SIZE, INPUT_SIZE), e1.shape
    assert e1.dtype == torch.float32
    assert torch.equal(e1, e2), "eval transform must be deterministic"
    print(f"[OK] eval transform: shape={tuple(e1.shape)}, deterministic")

    torch.manual_seed(0)
    t1 = train_t(pil_image)
    t2 = train_t(pil_image)
    assert t1.shape == (3, INPUT_SIZE, INPUT_SIZE)
    assert not torch.equal(t1, t2), "train transform must be stochastic"
    print(f"[OK] train transform: shape={tuple(t1.shape)}, stochastic")

    print(
        f"eval per-channel mean: "
        f"{[round(float(e1[c].mean()), 3) for c in range(3)]}"
    )
    print(
        f"eval per-channel std:  "
        f"{[round(float(e1[c].std()), 3) for c in range(3)]}"
    )
    assert e1.min() < 0, "Normalize not applied — tensor still in [0,1]"

    print("\nTransforms sanity check: PASSED")


if __name__ == "__main__":
    main()
