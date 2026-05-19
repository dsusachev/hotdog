"""Single-image inference (task #41).

The Predictor loads a packaged artifact once and exposes a predict() method
that runs preprocessing + forward + softmax on one image. Designed so the
FastAPI service (task #50) can hold one long-lived Predictor.

Top-k extraction and threshold logic are added in tasks #42 and #43; here
we only return the top-1 prediction.
"""
from __future__ import annotations

import time
from io import BytesIO
from pathlib import Path
from typing import Union

import torch
import torch.nn.functional as F
from PIL import Image

from src.artifact import (
    build_eval_transform_from_artifact,
    build_model_from_artifact,
    class_names_from_artifact,
    load_artifact,
)
from src.train import pick_device

ImageInput = Union[Image.Image, str, Path, bytes]


class Predictor:
    def __init__(
        self,
        artifact_path: str | Path,
        device: torch.device | None = None,
    ) -> None:
        self.artifact_path = Path(artifact_path)
        self.artifact = load_artifact(self.artifact_path)
        self.device = device or pick_device()
        self.model = build_model_from_artifact(self.artifact).to(self.device).eval()
        self.transform = build_eval_transform_from_artifact(self.artifact)
        self.class_names = class_names_from_artifact(self.artifact)
        self.model_version = self.artifact["model_version"]
        self.threshold = self.artifact.get("threshold")  # None until task #44

    # ------------------------------------------------------------------ image IO

    @staticmethod
    def _load_image(image: ImageInput) -> Image.Image:
        if isinstance(image, Image.Image):
            img = image
        elif isinstance(image, (str, Path)):
            img = Image.open(image)
        elif isinstance(image, (bytes, bytearray)):
            img = Image.open(BytesIO(image))
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
        return img.convert("RGB")

    # --------------------------------------------------------------- prediction

    def _label_dict(self, class_id: int, confidence: float) -> dict:
        return {
            "category": self.class_names[class_id],
            "category_id": class_id,
            "confidence": confidence,
        }

    @torch.no_grad()
    def predict(self, image: ImageInput, top_k: int = 3) -> dict:
        """Single-image prediction with top-k (ml_aproach.md §10).

        Returns:
            {
                "prediction": {category, category_id, confidence},   # top-1
                "top_k": [ {category, category_id, confidence}, ... ], # length=top_k, desc-sorted
                "model_version": str,
                "inference_time_ms": int,
            }
        Note: top_k[0] intentionally duplicates `prediction` — keeps the
        frontend loop uniform regardless of is_unknown (task #43).
        """
        if not 1 <= top_k <= len(self.class_names):
            raise ValueError(
                f"top_k must be in [1, {len(self.class_names)}], got {top_k}"
            )

        t0 = time.perf_counter()
        img = self._load_image(image)
        x = self.transform(img).unsqueeze(0).to(self.device)
        logits = self.model(x)
        probs = F.softmax(logits, dim=1)[0]

        top_probs, top_indices = probs.topk(top_k)
        top_probs = top_probs.tolist()
        top_indices = [int(i) for i in top_indices.tolist()]

        top_k_list = [
            self._label_dict(idx, float(p))
            for idx, p in zip(top_indices, top_probs)
        ]
        prediction = dict(top_k_list[0])  # copy so callers can mutate safely

        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        return {
            "prediction": prediction,
            "top_k": top_k_list,
            "model_version": self.model_version,
            "inference_time_ms": elapsed_ms,
        }
