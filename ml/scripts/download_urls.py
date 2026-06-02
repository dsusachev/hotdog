"""Point-wise image downloader for the own mini test set (task #45).

Reads a CSV of (class_name, url) pairs and downloads each URL into
ml/own_test_set/<class_name>/. Auto-numbers files so consecutive runs
don't overwrite. Validates that each downloaded file is a real image
that PIL can decode.

This is NOT a scraper. You bring URLs of single product images from sites
that allow direct image access. For the grocery MVP we recommend:
  - OpenFoodFacts (https://world.openfoodfacts.org, has API + RU products)
  - Direct product-image CDN URLs you copy by hand
We do not crawl pages or bypass anti-bot — both for legal hygiene and
because it is a deep side-project on its own.

CSV format (header required):
    class_name,url
    Apple,https://example.com/path/red-apple.jpg
    Milk,https://example.com/path/prostokvashino-milk.jpg

Usage:
    python ml/scripts/download_urls.py --csv urls.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.evaluate import load_class_names  # noqa: E402

DEFAULT_OUT_ROOT = REPO_ROOT / "ml" / "own_test_set"
DEFAULT_DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"

EXT_BY_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
USER_AGENT = "Mozilla/5.0 (hotdog-ml-research)"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--csv", type=Path, required=True, help="CSV with header class_name,url"
    )
    p.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    p.add_argument(
        "--dataset-root",
        type=Path,
        default=DEFAULT_DATASET_ROOT,
        help="Used to validate class_name against classes.csv",
    )
    p.add_argument("--timeout", type=int, default=15)
    p.add_argument(
        "--min-size-kb",
        type=int,
        default=10,
        help="Reject downloads smaller than this — usually error pages",
    )
    return p.parse_args()


def _next_index(folder: Path) -> int:
    existing = [
        int(p.stem) for p in folder.iterdir() if p.is_file() and p.stem.isdigit()
    ]
    return (max(existing) + 1) if existing else 1


def _ext_from_response(resp: requests.Response, url: str) -> str:
    ct = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if ct in EXT_BY_MIME:
        return EXT_BY_MIME[ct]
    # Fallback: guess from URL path.
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return ".jpg"  # last-resort default


def main() -> None:
    args = parse_args()
    valid_class_names = set(load_class_names(args.dataset_root))
    args.out_root.mkdir(parents=True, exist_ok=True)

    # utf-8-sig strips a BOM if the CSV was saved by Excel / a Windows editor.
    rows = list(csv.DictReader(args.csv.open(encoding="utf-8-sig")))
    if not rows or set(rows[0].keys()) != {"class_name", "url"}:
        raise SystemExit(
            f"CSV must have exactly two columns: class_name,url. "
            f"Got: {set(rows[0].keys()) if rows else 'empty file'}"
        )

    n_ok = 0
    n_skip = 0
    for i, row in enumerate(rows, start=1):
        cname = row["class_name"].strip()
        url = row["url"].strip()
        if cname not in valid_class_names:
            print(f"[{i}/{len(rows)}] SKIP unknown class '{cname}'")
            n_skip += 1
            continue

        out_dir = args.out_root / cname
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            resp = requests.get(
                url,
                timeout=args.timeout,
                headers={"User-Agent": USER_AGENT},
                stream=True,
            )
            resp.raise_for_status()
            data = resp.content
            if len(data) < args.min_size_kb * 1024:
                print(
                    f"[{i}/{len(rows)}] SKIP {cname}: too small "
                    f"({len(data)} bytes) — likely an error page"
                )
                n_skip += 1
                continue

            ext = _ext_from_response(resp, url)
            idx = _next_index(out_dir)
            out_path = out_dir / f"{idx:04d}{ext}"
            out_path.write_bytes(data)

            # Verify it actually decodes as an image.
            with Image.open(out_path) as img:
                img.verify()

            print(
                f"[{i}/{len(rows)}] OK   {cname}: {out_path.name} "
                f"({len(data) // 1024} KB)"
            )
            n_ok += 1
        except Exception as e:
            print(f"[{i}/{len(rows)}] FAIL {cname}: {e}")
            n_skip += 1

    print(f"\nDownloaded: {n_ok}, skipped: {n_skip}")


if __name__ == "__main__":
    main()
