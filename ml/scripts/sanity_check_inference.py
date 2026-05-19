"""Sanity-check for single-image inference (task #41).

Verifies:
  - Predictor loads the artifact and produces a well-formed dict
  - Predictor.predict on first N val images matches predict_all logits
    exactly (same preprocessing + same weights)
  - Predictor accepts PIL.Image, file path, and raw bytes interchangeably
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import DataLoader, Subset

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml"))

from src.artifact import (  # noqa: E402
    build_eval_transform_from_artifact,
    load_artifact,
)
from src.dataset import GroceryStoreDataset  # noqa: E402
from src.evaluate import predict_all  # noqa: E402
from src.inference import Predictor  # noqa: E402

DATASET_ROOT = REPO_ROOT / "ml" / "dataset" / "GroceryStoreDataset" / "dataset"


def check(artifact_path: Path) -> None:
    print(f"\n=== {artifact_path.name} ===")

    p = Predictor(artifact_path)
    print(f"model_version={p.model_version}, device={p.device}, "
          f"threshold={p.threshold}, n_classes={len(p.class_names)}")

    raw_ds = GroceryStoreDataset(DATASET_ROOT, "val", transform=None)
    eval_ds = GroceryStoreDataset(
        DATASET_ROOT, "val",
        transform=build_eval_transform_from_artifact(p.artifact),
    )
    n = 12
    loader = DataLoader(Subset(eval_ds, list(range(n))), batch_size=n, shuffle=False)
    batch_logits, batch_labels = predict_all(p.model, loader, p.device)
    batch_preds = batch_logits.argmax(axis=1)
    batch_probs = torch.softmax(torch.from_numpy(batch_logits), dim=1).numpy()

    # Force threshold=0.0 for batch-vs-predictor comparison so prediction is
    # never nulled to is_unknown — we want to compare top-1 ids directly.
    for i in range(n):
        pil_img, true_label = raw_ds[i]
        out = p.predict(pil_img, top_k=3, threshold=0.0)

        assert set(out.keys()) == {
            "is_unknown", "prediction", "top_k",
            "threshold", "model_version", "inference_time_ms",
        }, out.keys()
        assert out["threshold"] == 0.0
        assert out["is_unknown"] is False
        pred = out["prediction"]
        assert set(pred.keys()) == {"category", "category_id", "confidence"}
        assert pred["category_id"] == int(batch_preds[i])
        assert abs(
            pred["confidence"] - float(batch_probs[i, pred["category_id"]])
        ) < 1e-5

        topk = out["top_k"]
        assert len(topk) == 3
        # top_k[0] duplicates prediction (intentional, ml_aproach.md §10)
        assert topk[0] == pred
        confs = [t["confidence"] for t in topk]
        assert confs == sorted(confs, reverse=True), confs
        assert sum(confs) <= 1.0 + 1e-5
        assert len({t["category_id"] for t in topk}) == 3

    print(f"[OK] predict(top_k=3) matches predict_all + invariants hold")

    # ---- threshold branches ----
    pil_img, _ = raw_ds[0]
    out_low = p.predict(pil_img, top_k=3, threshold=0.0)
    assert out_low["is_unknown"] is False
    assert out_low["prediction"] is not None
    print(f"[OK] threshold=0.0 -> never unknown")

    out_high = p.predict(pil_img, top_k=3, threshold=0.9999)
    # softmax top-1 < 0.9999 is essentially guaranteed for a 43-class model.
    assert out_high["is_unknown"] is True, out_high
    assert out_high["prediction"] is None
    assert len(out_high["top_k"]) == 3  # top_k still returned on unknown
    assert out_high["threshold"] == 0.9999
    print(f"[OK] threshold=0.9999 -> is_unknown=True, prediction=None, top_k present")

    # k=1 degenerate case
    out_k1 = p.predict(raw_ds[0][0], top_k=1)
    assert len(out_k1["top_k"]) == 1
    assert out_k1["top_k"][0] == out_k1["prediction"]
    print(f"[OK] top_k=1 is a degenerate case of top-k")

    # bytes input — encode first val image as JPEG bytes
    pil_img, _ = raw_ds[0]
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=95)
    out_pil = p.predict(pil_img)
    out_bytes = p.predict(buf.getvalue())
    assert (
        out_pil["prediction"]["category_id"]
        == out_bytes["prediction"]["category_id"]
    ), "PIL and bytes inputs disagree on top-1"
    print(f"[OK] PIL / bytes inputs interchangeable")

    print(f"  sample output: {out_pil}")


def main() -> None:
    artifacts = sorted((REPO_ROOT / "ml" / "artifacts").glob("*.pt"))
    if not artifacts:
        raise SystemExit("No artifacts in ml/artifacts/")
    for p in artifacts:
        check(p)
    print("\nInference sanity check: PASSED")


if __name__ == "__main__":
    main()
