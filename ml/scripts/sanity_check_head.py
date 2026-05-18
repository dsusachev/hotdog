"""Sanity-check for the new classifier head (task #37).

Verifies for both EfficientNet-B0 and ResNet50:
  - forward output shape is (B, NUM_COARSE_CLASSES) instead of (B, 1000)
  - head is the new Dropout + Linear sequence
  - set_backbone_trainable(False) freezes backbone but leaves head trainable
  - set_backbone_trainable(True) unfreezes everything
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.dataset import NUM_COARSE_CLASSES  # noqa: E402
from src.model import (  # noqa: E402
    HEAD_DROPOUT,
    build_model,
    set_backbone_trainable,
)


def _count_trainable(model) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def main() -> None:
    x = torch.randn(2, 3, 224, 224)

    for name in ("efficientnet_b0", "resnet50"):
        model = build_model(name, num_classes=NUM_COARSE_CLASSES, pretrained=True)
        model.eval()

        with torch.no_grad():
            y = model(x)
        assert y.shape == (2, NUM_COARSE_CLASSES), (name, y.shape)

        head = model.classifier if name == "efficientnet_b0" else model.fc
        assert isinstance(head, torch.nn.Sequential), (name, type(head))
        assert isinstance(head[0], torch.nn.Dropout)
        assert head[0].p == HEAD_DROPOUT
        assert isinstance(head[1], torch.nn.Linear)
        assert head[1].out_features == NUM_COARSE_CLASSES

        total = sum(p.numel() for p in model.parameters())
        before = _count_trainable(model)
        set_backbone_trainable(model, name, trainable=False)
        after_freeze = _count_trainable(model)
        set_backbone_trainable(model, name, trainable=True)
        after_unfreeze = _count_trainable(model)

        head_params = sum(p.numel() for p in head.parameters())

        assert before == total, f"{name}: initial state should be fully trainable"
        assert after_freeze == head_params, (
            f"{name}: after freeze, only head should remain trainable "
            f"(got {after_freeze} vs head {head_params})"
        )
        assert after_unfreeze == total, f"{name}: unfreeze must restore all params"

        print(
            f"[OK] {name}: out={tuple(y.shape)}, head_in={head[1].in_features}, "
            f"head_params={head_params:,}, total={total:,}"
        )

    print("\nHead-replacement sanity check: PASSED")


if __name__ == "__main__":
    main()
