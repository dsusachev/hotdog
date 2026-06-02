"""Loader for our own mini test set (task #45).

Folder layout (ImageFolder-style with explicit coarse-name folders):

    ml/own_test_set/
        Apple/
            0001.jpg
            0002.jpg
            ...
        Milk/
            ...
        Yoghurt/
            ...

Subfolder names MUST match the Coarse Class Name column in classes.csv
(case-sensitive). Unknown folders raise — silent label mismatches are worse
than a crash.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from PIL import Image
from torch.utils.data import Dataset

from src.evaluate import load_class_names

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


class OwnSample(NamedTuple):
    file_path: Path
    coarse_label: int
    class_name: str


class OwnMiniDataset(Dataset):
    """Folder dataset for our own photos, mapped to grocery-store coarse IDs."""

    def __init__(
        self,
        root: str | Path,
        dataset_root: str | Path,
        transform: Callable | None = None,
        allow_empty: bool = False,
    ) -> None:
        self.root = Path(root)
        if not self.root.exists():
            raise FileNotFoundError(f"own-mini-set root does not exist: {self.root}")

        coarse_names = load_class_names(dataset_root)
        self.name_to_id = {name: i for i, name in enumerate(coarse_names)}

        self.samples: list[OwnSample] = []
        for class_dir in sorted(self.root.iterdir()):
            if not class_dir.is_dir():
                continue
            if class_dir.name not in self.name_to_id:
                raise ValueError(
                    f"Folder '{class_dir.name}' does not match any coarse class. "
                    f"Expected one of: {sorted(self.name_to_id)}"
                )
            label = self.name_to_id[class_dir.name]
            for img_path in sorted(class_dir.iterdir()):
                if img_path.suffix.lower() not in VALID_EXTENSIONS:
                    continue
                self.samples.append(OwnSample(img_path, label, class_dir.name))

        if not self.samples and not allow_empty:
            raise ValueError(
                f"No images found in {self.root}. Expected files in {VALID_EXTENSIONS}."
            )

        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        s = self.samples[idx]
        with Image.open(s.file_path) as img:
            image = img.convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, s.coarse_label

    # Helpers for reports — keep file paths so we can show failure examples.

    def sample_meta(self, idx: int) -> OwnSample:
        return self.samples[idx]
