"""Production-ready model artifact (task #40).

Bundles weights + preprocessing config + class names + metrics + version into
a single .pt file that inference code (task #41+) and the FastAPI service
(task #50) can load with one call.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import torch
import torch.nn as nn

from torchvision import transforms

from src.evaluate import load_class_names
from src.model import Backbone, build_model
from src.transforms import EVAL_RESIZE, IMAGENET_MEAN, IMAGENET_STD, INPUT_SIZE

ARTIFACT_SCHEMA_VERSION = 1


def build_artifact_dict(
    model_state: dict,
    backbone: Backbone,
    num_classes: int,
    class_names: list[str],
    metrics: dict,
    train_config: dict,
    source_run_dir: str | Path,
    model_version: str,
) -> dict:
    """Compose the artifact dict to be torch.save'd."""
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "model_state": model_state,
        "model_version": model_version,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "backbone": backbone,
        "num_classes": num_classes,
        "input_size": INPUT_SIZE,
        "preprocessing": {
            "resize": EVAL_RESIZE,
            "crop": INPUT_SIZE,
            "mean": list(IMAGENET_MEAN),
            "std": list(IMAGENET_STD),
        },
        "class_id_to_name": {str(i): n for i, n in enumerate(class_names)},
        "metrics": metrics,
        "threshold": None,  # set by task #44
        "train_config": train_config,
        "source_run_dir": str(source_run_dir),
    }


def save_artifact(artifact: dict, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(artifact, out_path)
    return out_path


def load_artifact(path: str | Path, map_location: str | torch.device = "cpu") -> dict:
    """Load and validate an artifact. Returns the dict; does NOT instantiate a model."""
    artifact = torch.load(path, map_location=map_location, weights_only=False)
    schema = artifact.get("schema_version")
    if schema != ARTIFACT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported artifact schema_version={schema}, "
            f"this code understands {ARTIFACT_SCHEMA_VERSION}"
        )
    required = {"model_state", "model_version", "backbone", "num_classes",
                "preprocessing", "class_id_to_name"}
    missing = required - set(artifact.keys())
    if missing:
        raise ValueError(f"Artifact at {path} is missing fields: {missing}")
    return artifact


def build_model_from_artifact(artifact: dict) -> nn.Module:
    """Instantiate a torch model and load weights from a parsed artifact."""
    model = build_model(
        artifact["backbone"],
        num_classes=artifact["num_classes"],
        pretrained=False,
    )
    model.load_state_dict(artifact["model_state"])
    model.eval()
    return model


def class_names_from_artifact(artifact: dict) -> list[str]:
    """Return class names ordered by class_id."""
    mapping = artifact["class_id_to_name"]
    n = artifact["num_classes"]
    return [mapping[str(i)] for i in range(n)]


def build_eval_transform_from_artifact(artifact: dict) -> transforms.Compose:
    """Build eval transform using preprocessing config stored in the artifact.

    Inference must use the *exact* preprocessing the model was evaluated with,
    so we read params from the artifact instead of from src.transforms — this
    way changing src.transforms in the future does not silently break inference.
    """
    pp = artifact["preprocessing"]
    return transforms.Compose([
        transforms.Resize(pp["resize"]),
        transforms.CenterCrop(pp["crop"]),
        transforms.ToTensor(),
        transforms.Normalize(pp["mean"], pp["std"]),
    ])
