"""Validate own_test_set/ before evaluation (task #45).

Verifies:
  - all subfolder names match coarse class names from classes.csv
  - every file decodes as an image
  - prints per-class counts so the team sees coverage at a glance
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.own_dataset import OwnMiniDataset  # noqa: E402

OWN_ROOT = REPO_ROOT / "ml" / "own_test_set"
DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"

EXPECTED_CLASSES = {
    "Apple",
    "Banana",
    "Orange",
    "Pear",
    "Tomato",
    "Pepper",
    "Potato",
    "Milk",
    "Juice",
    "Yoghurt",
}


def main() -> None:
    if not OWN_ROOT.exists():
        raise SystemExit(f"Missing {OWN_ROOT}")
    ds = OwnMiniDataset(OWN_ROOT, DATASET_ROOT, transform=None, allow_empty=True)
    counts = Counter(s.class_name for s in ds.samples)

    print(f"Loaded {len(ds)} images across {len(counts)} classes\n")
    for cname in sorted(EXPECTED_CLASSES):
        n = counts.get(cname, 0)
        status = "OK  " if 5 <= n <= 30 else ("LOW " if n < 5 else "WARN")
        print(f"  [{status}] {cname:10s} {n}")

    missing = EXPECTED_CLASSES - set(counts.keys())
    extra = set(counts.keys()) - EXPECTED_CLASSES
    if missing:
        print(f"\nMissing classes (no photos yet): {sorted(missing)}")
    if extra:
        print(f"\nUnexpected classes: {sorted(extra)}")

    # Try opening every image — catch broken files early.
    n_broken = 0
    for s in ds.samples:
        try:
            ds[ds.samples.index(s)]
        except Exception as e:
            print(f"  BROKEN: {s.file_path} ({e})")
            n_broken += 1
    if n_broken:
        raise SystemExit(f"{n_broken} broken file(s)")

    if not missing and all(counts[c] >= 5 for c in EXPECTED_CLASSES):
        print("\nOwn-set sanity check: PASSED")
    else:
        print("\nOwn-set sanity check: NEEDS MORE PHOTOS")


if __name__ == "__main__":
    main()
