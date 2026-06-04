"""Dataset of iconic (catalog) images from classes.csv — public OOD split.

Each fine class has exactly one iconic image: a clean, white-background catalog
photo. These images are out-of-distribution relative to the training data (which
are natural in-store photos), making this split useful as a public OOD test.

One sample per fine class → mapped to its coarse label.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import torch
from PIL import Image
from torch.utils.data import Dataset


@dataclass(frozen=True)
class IconicSample:
    file_path: Path
    fine_class_name: str
    coarse_label: int
    coarse_class_name: str


class IconicOodDataset(Dataset):
    """One iconic image per fine class, labeled by coarse ID.

    Args:
        dataset_root: path to GroceryStoreDataset/dataset/
        transform:    eval transform (same as used for val/test)
    """

    def __init__(
        self,
        dataset_root: str | Path,
        transform: Callable | None = None,
    ) -> None:
        self.dataset_root = Path(dataset_root)
        classes_csv = self.dataset_root / "classes.csv"
        if not classes_csv.exists():
            raise FileNotFoundError(classes_csv)

        self.samples: list[IconicSample] = []
        with classes_csv.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                iconic_rel = row["Iconic Image Path (str)"].lstrip("/")
                img_path = self.dataset_root / iconic_rel
                if not img_path.exists():
                    raise FileNotFoundError(
                        f"Iconic image missing: {img_path}\n"
                        f"  (classes.csv row: {row['Class Name (str)']})"
                    )
                self.samples.append(
                    IconicSample(
                        file_path=img_path,
                        fine_class_name=row["Class Name (str)"],
                        coarse_label=int(row["Coarse Class ID (int)"]),
                        coarse_class_name=row["Coarse Class Name (str)"],
                    )
                )

        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor | Image.Image, int]:
        s = self.samples[idx]
        with Image.open(s.file_path) as img:
            image = img.convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, s.coarse_label

    def sample_meta(self, idx: int) -> IconicSample:
        return self.samples[idx]
