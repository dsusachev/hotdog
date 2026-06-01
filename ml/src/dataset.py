from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

NUM_COARSE_CLASSES = 43


@dataclass(frozen=True)
class Sample:
    rel_path: str
    coarse_label: int


def _parse_split_file(split_file: Path) -> list[Sample]:
    samples: list[Sample] = []
    with split_file.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 3:
                raise ValueError(f"Bad line in {split_file}: {raw!r}")
            rel_path, _fine, coarse = parts
            samples.append(Sample(rel_path=rel_path, coarse_label=int(coarse)))
    return samples


class GroceryStoreDataset(Dataset):
    """Author-provided splits of the Grocery Store Dataset.

    Returns (image_tensor_or_PIL, coarse_label). Fine label is dropped — MVP
    targets coarse-grained (42 classes), per ml_aproach.md §3.1.
    """

    def __init__(
        self,
        dataset_root: str | Path,
        split: str,
        transform: Callable | None = None,
    ) -> None:
        if split not in {"train", "val", "test"}:
            raise ValueError(f"split must be train|val|test, got {split!r}")

        self.dataset_root = Path(dataset_root)
        split_file = self.dataset_root / f"{split}.txt"
        if not split_file.exists():
            raise FileNotFoundError(split_file)

        self.samples = _parse_split_file(split_file)
        self.transform = transform
        self.split = split

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor | Image.Image, int]:
        sample = self.samples[idx]
        img_path = self.dataset_root / sample.rel_path
        with Image.open(img_path) as img:
            image = img.convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, sample.coarse_label


def build_dataloaders(
    dataset_root: str | Path,
    train_transform: Callable | None = None,
    eval_transform: Callable | None = None,
    batch_size: int = 32,
    num_workers: int = 4,
    pin_memory: bool = True,
) -> dict[str, DataLoader]:
    train_ds = GroceryStoreDataset(dataset_root, "train", transform=train_transform)
    val_ds = GroceryStoreDataset(dataset_root, "val", transform=eval_transform)
    test_ds = GroceryStoreDataset(dataset_root, "test", transform=eval_transform)

    common = dict(batch_size=batch_size, num_workers=num_workers, pin_memory=pin_memory)
    return {
        "train": DataLoader(train_ds, shuffle=True, drop_last=True, **common),
        "val": DataLoader(val_ds, shuffle=False, drop_last=False, **common),
        "test": DataLoader(test_ds, shuffle=False, drop_last=False, **common),
    }
