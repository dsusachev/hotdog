"""Launch the ML inference service on :8001 (settings.ML_SERVICE_URL).

    python ml/serve.py

Override the model with ML_ARTIFACT_PATH and the port with ML_SERVICE_PORT.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_ROOT))

import uvicorn  # noqa: E402

from scripts.download_model import ensure_artifact  # noqa: E402
from service.app import app  # noqa: E402

if __name__ == "__main__":
    # Fetch the default artifact on demand so the service works on a fresh
    # clone. A custom ML_ARTIFACT_PATH means the user manages their own file.
    if not os.environ.get("ML_ARTIFACT_PATH"):
        ensure_artifact()
    port = int(os.environ.get("ML_SERVICE_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
