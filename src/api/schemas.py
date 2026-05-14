from pydantic import BaseModel
from typing import List


class TopPrediction(BaseModel):
    category: str
    confidence: float


class ClassifyResponse(BaseModel):
    status: str                        # "ok" | "unknown"
    is_unknown: bool                   # True если объект не распознан
    category: str | None               # Топ-1 категория
    confidence: float | None           # Уверенность топ-1 (0.0 - 1.0)
    top_k: List[TopPrediction]         # Топ-3 предсказания
    mock: bool = False                 # True если ML Service недоступен


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
