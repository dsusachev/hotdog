from __future__ import annotations

from torchvision import transforms

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

INPUT_SIZE = 224
EVAL_RESIZE = 256


def build_train_transform() -> transforms.Compose:
    """Train-time augmentations per ml_aproach.md §7.

    Resize is handled by RandomResizedCrop — no separate Resize step.
    """
    return transforms.Compose(
        [
            transforms.RandomResizedCrop(INPUT_SIZE, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(
                brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1
            ),
            transforms.RandomRotation(degrees=15),
            transforms.RandomPerspective(p=0.3),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def build_eval_transform() -> transforms.Compose:
    """Deterministic val/test transform: ImageNet-style 256 -> center 224."""
    return transforms.Compose(
        [
            transforms.Resize(EVAL_RESIZE),
            transforms.CenterCrop(INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )
