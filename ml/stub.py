"""Stub ML service — returns a fixed mock response while the real model is unavailable."""

from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="HotDog ML Stub", version="stub")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "model_version": "stub"}


@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    return {
        "category": "Apple",
        "confidence": 0.95,
        "top_k": [
            {"category": "Apple", "confidence": 0.95},
            {"category": "Banana", "confidence": 0.03},
            {"category": "Orange", "confidence": 0.02},
        ],
        "is_unknown": False,
        "model_version": "stub",
        "inference_time_ms": 5.0,
    }
