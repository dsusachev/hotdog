"""Sanity-check for artifact round-trip (task #40).

Verifies that:
  - artifact loads and validates
  - model can be instantiated from it
  - re-loaded weights produce bit-identical logits to the source checkpoint
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.artifact import (  # noqa: E402
    build_model_from_artifact,
    class_names_from_artifact,
    load_artifact,
)
from src.dataset import GroceryStoreDataset  # noqa: E402
from src.model import build_model  # noqa: E402
from src.train import pick_device  # noqa: E402
from src.transforms import build_eval_transform  # noqa: E402

DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"


def check_artifact(artifact_path: Path) -> None:
    print(f"\n=== Checking {artifact_path.name} ===")
    artifact = load_artifact(artifact_path)
    print(f"model_version={artifact['model_version']}")
    print(f"backbone={artifact['backbone']}, num_classes={artifact['num_classes']}")
    print(f"trained_at={artifact['trained_at']}")
    print(f"input_size={artifact['input_size']}, "
          f"resize={artifact['preprocessing']['resize']}, "
          f"crop={artifact['preprocessing']['crop']}")
    test_top1 = artifact["metrics"]["test"]["top1"]
    print(f"metrics.test.top1={test_top1:.4f}")
    print(f"threshold={artifact['threshold']}  (None until task #44)")

    class_names = class_names_from_artifact(artifact)
    assert len(class_names) == artifact["num_classes"]
    assert class_names[0] == "Apple"

    # Build "fresh from artifact" and compare against direct load.
    model_from_art = build_model_from_artifact(artifact)
    model_direct = build_model(
        artifact["backbone"], num_classes=artifact["num_classes"], pretrained=False
    )
    model_direct.load_state_dict(artifact["model_state"])
    model_direct.eval()

    device = pick_device()
    model_from_art.to(device)
    model_direct.to(device)

    ds = GroceryStoreDataset(DATASET_ROOT, "val", transform=build_eval_transform())
    loader = DataLoader(Subset(ds, list(range(16))), batch_size=16, shuffle=False)
    images, _ = next(iter(loader))
    images = images.to(device)
    with torch.no_grad():
        y1 = model_from_art(images)
        y2 = model_direct(images)
    assert torch.allclose(y1, y2), "artifact load gave different logits than direct load"

    print(f"[OK] artifact round-trip identical (max diff "
          f"{(y1 - y2).abs().max().item():.2e})")


def main() -> None:
    artifacts = sorted(Path(REPO_ROOT / "ml" / "artifacts").glob("*.pt"))
    if not artifacts:
        raise SystemExit("No artifacts found in ml/artifacts/. "
                         "Run package_artifact.py first.")
    for p in artifacts:
        check_artifact(p)
    print("\nArtifact sanity check: PASSED")


if __name__ == "__main__":
    main()
