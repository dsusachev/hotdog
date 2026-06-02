from __future__ import annotations

from typing import Literal

import torch.nn as nn
from torchvision.models import (
    EfficientNet_B0_Weights,
    ResNet50_Weights,
    efficientnet_b0,
    resnet50,
)

from src.dataset import NUM_COARSE_CLASSES

Backbone = Literal["efficientnet_b0", "resnet50"]

HEAD_DROPOUT = 0.3


def build_backbone(name: Backbone, pretrained: bool = True) -> nn.Module:
    """Load a torchvision backbone with ImageNet weights.

    Returns the model with its original ImageNet classifier head intact —
    head replacement under our num_classes happens in build_model().
    """
    if name == "efficientnet_b0":
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        return efficientnet_b0(weights=weights)
    if name == "resnet50":
        weights = ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
        return resnet50(weights=weights)
    raise ValueError(f"Unknown backbone: {name}")


def _replace_head(model: nn.Module, name: Backbone, num_classes: int) -> nn.Module:
    if name == "efficientnet_b0":
        in_features = model.classifier[1].in_features  # 1280
        model.classifier = nn.Sequential(
            nn.Dropout(p=HEAD_DROPOUT),
            nn.Linear(in_features, num_classes),
        )
    elif name == "resnet50":
        in_features = model.fc.in_features  # 2048
        model.fc = nn.Sequential(
            nn.Dropout(p=HEAD_DROPOUT),
            nn.Linear(in_features, num_classes),
        )
    else:
        raise ValueError(f"Unknown backbone: {name}")
    return model


def build_model(
    name: Backbone,
    num_classes: int = NUM_COARSE_CLASSES,
    pretrained: bool = True,
) -> nn.Module:
    """Build a transfer-learning classifier: pretrained backbone + new head."""
    model = build_backbone(name, pretrained=pretrained)
    return _replace_head(model, name, num_classes)


def set_backbone_trainable(model: nn.Module, name: Backbone, trainable: bool) -> None:
    """Freeze or unfreeze the backbone, keeping the new head trainable.

    Used for the two-stage transfer-learning strategy (task #38):
      stage 1 (feature extraction): trainable=False
      stage 2 (fine-tuning):        trainable=True (or unfreeze top blocks)
    """
    if name == "efficientnet_b0":
        head = model.classifier
    elif name == "resnet50":
        head = model.fc
    else:
        raise ValueError(f"Unknown backbone: {name}")

    head_param_ids = {id(p) for p in head.parameters()}
    for p in model.parameters():
        if id(p) not in head_param_ids:
            p.requires_grad = trainable
