"""Download trained model artifacts from the GitHub Release.

The .pt files are too large for git (gitignored), so they live as assets on the
`models-v1` release of dsusachev/hotdog and are fetched on demand into
ml/artifacts/. This makes the real ML service work for anyone who clones the
repo — no manual Google Drive step.

Usage:
    python ml/scripts/download_model.py                 # default (resnet50)
    python ml/scripts/download_model.py --model efficientnet
    python ml/scripts/download_model.py --all
    python ml/scripts/download_model.py --force         # re-download

Programmatic:
    from scripts.download_model import ensure_artifact
    path = ensure_artifact()        # returns Path, downloads if missing
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]  # .../ml
ARTIFACTS_DIR = ML_ROOT / "artifacts"

RELEASE_BASE = "https://github.com/dsusachev/hotdog/releases/download/models-v1"

# filename -> sha256, keyed by short model name. The .pt embeds its own
# threshold, so the service needs nothing else.
MODELS: dict[str, dict[str, str]] = {
    "resnet50": {
        "filename": "resnet50_v1_20260519.pt",
        "sha256": "78b145d7510931165426adaf33d91850b574739fe08c1b4fbaf113d73425f95e",
    },
    "efficientnet": {
        "filename": "efficientnet_b0_v1_20260519.pt",
        "sha256": "69ed4af2d9023376eb6a3e66aedb6516d3f0e15dee36f0a2d083989bbbad905b",
    },
}

DEFAULT_MODEL = "resnet50"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    """Stream url -> dest atomically, printing a progress bar."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "hotdog-download-model"})
    with urllib.request.urlopen(req) as resp:  # noqa: S310 - fixed GitHub URL
        total = int(resp.headers.get("Content-Length", 0))
        fd, tmp_name = tempfile.mkstemp(dir=dest.parent, suffix=".part")
        tmp = Path(tmp_name)
        done = 0
        try:
            with os.fdopen(fd, "wb") as out:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = done * 100 // total
                        bar = "#" * (pct // 4)
                        sys.stdout.write(
                            f"\r  {dest.name}: [{bar:<25}] {pct:3d}% "
                            f"({done >> 20}/{total >> 20} MB)"
                        )
                        sys.stdout.flush()
            sys.stdout.write("\n")
            tmp.chmod(0o644)  # mkstemp defaults to 0600; match a normal file
            tmp.replace(dest)  # atomic on same filesystem
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise


def ensure_artifact(
    model: str = DEFAULT_MODEL,
    dest_dir: Path = ARTIFACTS_DIR,
    *,
    force: bool = False,
    verify: bool = True,
) -> Path:
    """Return the local path to the artifact, downloading it if absent.

    Idempotent: a present file with the right checksum is left untouched.
    Raises on checksum mismatch so a corrupt download never reaches the model.
    """
    if model not in MODELS:
        raise ValueError(f"Unknown model {model!r}; choose from {list(MODELS)}")
    spec = MODELS[model]
    dest = dest_dir / spec["filename"]
    expected = spec["sha256"]

    if dest.exists() and not force:
        if not verify or _sha256(dest) == expected:
            return dest
        print(f"  checksum mismatch for existing {dest.name}, re-downloading...")

    url = f"{RELEASE_BASE}/{spec['filename']}"
    print(f"Downloading {spec['filename']} from {url}")
    _download(url, dest)

    if verify:
        actual = _sha256(dest)
        if actual != expected:
            dest.unlink(missing_ok=True)
            raise RuntimeError(
                f"Checksum mismatch for {spec['filename']}: "
                f"expected {expected}, got {actual}"
            )
    print(f"  saved {dest} ({dest.stat().st_size >> 20} MB)")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Download ML model artifacts.")
    parser.add_argument(
        "--model",
        choices=list(MODELS),
        default=DEFAULT_MODEL,
        help=f"which model to fetch (default: {DEFAULT_MODEL})",
    )
    parser.add_argument("--all", action="store_true", help="fetch every model")
    parser.add_argument(
        "--force", action="store_true", help="re-download even if present"
    )
    args = parser.parse_args()

    targets = list(MODELS) if args.all else [args.model]
    for name in targets:
        ensure_artifact(name, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
