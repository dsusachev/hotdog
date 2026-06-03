"""Sanity-check for the Dataset/DataLoader pipeline (task #34).

Verifies:
  - len(train/val/test) match wc -l of the split files (2640 / 296 / 2485)
  - label range is [0, 41] (42 coarse classes)
  - one batch can be loaded
"""

from __future__ import annotations

import sys
from pathlib import Path

from torchvision import transforms

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.dataset import NUM_COARSE_CLASSES, build_dataloaders  # noqa: E402

DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"

EXPECTED_SIZES = {"train": 2640, "val": 296, "test": 2485}


def main() -> None:
    base_transform = transforms.Compose(
        [transforms.Resize((224, 224)), transforms.ToTensor()]
    )

    loaders = build_dataloaders(
        DATASET_ROOT,
        train_transform=base_transform,
        eval_transform=base_transform,
        batch_size=8,
        num_workers=0,
        pin_memory=False,
    )

    for split, expected in EXPECTED_SIZES.items():
        actual = len(loaders[split].dataset)
        status = "OK" if actual == expected else "FAIL"
        print(f"[{status}] {split}: {actual} (expected {expected})")
        assert actual == expected, f"{split} size mismatch"

    images, labels = next(iter(loaders["train"]))
    print(f"batch images: {tuple(images.shape)}, dtype={images.dtype}")
    print(f"batch labels: {tuple(labels.shape)}, dtype={labels.dtype}")
    print(f"label min/max: {int(labels.min())}/{int(labels.max())}")

    all_labels: list[int] = []
    for split in ("train", "val", "test"):
        ds = loaders[split].dataset
        all_labels.extend(s.coarse_label for s in ds.samples)
    lo, hi = min(all_labels), max(all_labels)
    n_unique = len(set(all_labels))
    print(f"coarse label range across all splits: [{lo}, {hi}], unique={n_unique}")
    assert lo == 0
    assert hi == NUM_COARSE_CLASSES - 1, f"max label {hi} != {NUM_COARSE_CLASSES - 1}"

    print("\nDataset pipeline sanity check: PASSED")


if __name__ == "__main__":
    main()
