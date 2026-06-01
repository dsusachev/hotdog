"""HTTP inference service — the missing 'task #50' referenced in inference.py.

Wraps the long-lived Predictor (ml/src/inference.py) in a FastAPI app exposing
POST /classify. It returns exactly the shape the backend's mlServiceClient
expects: top-level `category` + `confidence` plus `top_k: [{category, confidence}]`.
The Predictor nests the top-1 under `prediction` and adds `category_id`, so this
module also acts as the adapter between the two contracts.

Run it via ml/serve.py (listens on :8001, the address in settings.ML_SERVICE_URL).
"""
from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# The ML code imports as `src.*` (e.g. `from src.inference import Predictor`),
# where `src` resolves to ml/src once ml/ is on the path. This mirrors how the
# CLI in ml/scripts/predict.py bootstraps itself, and keeps this service a
# separate process so its `src` never collides with the backend's `src`.
ML_ROOT = Path(__file__).resolve().parents[1]  # .../ml
if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from fastapi import FastAPI, File, HTTPException, UploadFile  # noqa: E402

from src.inference import Predictor  # noqa: E402

DEFAULT_ARTIFACT = ML_ROOT / "artifacts" / "resnet50_v1_20260519.pt"
ARTIFACT_PATH = Path(os.environ.get("ML_ARTIFACT_PATH", str(DEFAULT_ARTIFACT)))

# Filled in at startup so a slow model load never blocks the first request mid-flight.
predictor: Predictor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    if not ARTIFACT_PATH.exists():
        raise RuntimeError(f"Artifact not found: {ARTIFACT_PATH}")
    predictor = Predictor(ARTIFACT_PATH)
    yield
    predictor = None


app = FastAPI(title="HotDog ML Inference", version="1.0.0", lifespan=lifespan)


def _adapt(result: dict) -> dict:
    """Map Predictor.predict() output to the backend's expected contract."""
    top_k = [
        {"category": p["category"], "confidence": p["confidence"]}
        for p in result["top_k"]
    ]
    top1 = top_k[0]
    return {
        "category": top1["category"],
        "confidence": top1["confidence"],
        "top_k": top_k,
        # extra context the backend currently ignores but the frontend may use later
        "is_unknown": result["is_unknown"],
        "model_version": result["model_version"],
        "inference_time_ms": result["inference_time_ms"],
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": predictor is not None,
        "model_version": getattr(predictor, "model_version", None),
        "artifact": str(ARTIFACT_PATH),
    }


@app.get("/classes")
def classes() -> dict:
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "model_version": predictor.model_version,
        "count": len(predictor.class_names),
        "classes": sorted(predictor.class_names),
    }


@app.post("/classify")
async def classify(file: UploadFile = File(...)) -> dict:
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        result = predictor.predict(image_bytes, top_k=3)
    except Exception as exc:  # noqa: BLE001 - surface any inference error as 500
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")

    return _adapt(result)
