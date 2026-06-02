"""Sanity-check for pretrained backbone loading (task #36).

Verifies:
  - both backbones load with ImageNet weights
  - param count is in the expected ballpark
  - a (1, 3, 224, 224) tensor passes through forward
  - output is the *ImageNet* head (1000 logits) — head replacement is task #37
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.model import build_backbone  # noqa: E402

EXPECTED_PARAM_RANGE = {
    "efficientnet_b0": (5_000_000, 5_500_000),
    "resnet50": (25_000_000, 26_000_000),
}


def main() -> None:
    x = torch.randn(2, 3, 224, 224)

    for name, (lo, hi) in EXPECTED_PARAM_RANGE.items():
        model = build_backbone(name, pretrained=True)
        model.eval()
        n_params = sum(p.numel() for p in model.parameters())
        assert lo <= n_params <= hi, (name, n_params)
        with torch.no_grad():
            y = model(x)
        assert y.shape == (2, 1000), (name, y.shape)
        print(f"[OK] {name}: params={n_params:,}, out={tuple(y.shape)}")

    print("\nModel sanity check: PASSED")


if __name__ == "__main__":
    main()
