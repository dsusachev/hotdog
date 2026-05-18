from __future__ import annotations

from typing import Literal

import torch.nn as nn
from torchvision.models import (
    EfficientNet_B0_Weights,
    ResNet50_Weights,
    efficientnet_b0,
    resnet50,
)

Backbone = Literal["efficientnet_b0", "resnet50"]


def build_backbone(name: Backbone, pretrained: bool = True) -> nn.Module:
    """Load a torchvision backbone with ImageNet weights.

    Returns the model with its original ImageNet classifier head intact —
    head replacement under our num_classes happens in task #37.
    """
    if name == "efficientnet_b0":
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        return efficientnet_b0(weights=weights)
    if name == "resnet50":
        weights = ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
        return resnet50(weights=weights)
    raise ValueError(f"Unknown backbone: {name}")
