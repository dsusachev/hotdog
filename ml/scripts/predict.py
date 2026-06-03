"""CLI single-image prediction (task #41).

Usage:
    python ml/scripts/predict.py \
        --artifact ml/artifacts/resnet50_v1_20260519.pt \
        --image path/to/photo.jpg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.inference import Predictor  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", type=Path, required=True)
    p.add_argument("--image", type=Path, required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    predictor = Predictor(args.artifact)
    result = predictor.predict(args.image)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
