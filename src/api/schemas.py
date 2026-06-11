from pydantic import BaseModel


class TopPrediction(BaseModel):
    category: str
    confidence: float


class ClassifyResponse(BaseModel):
    status: str  # "ok" | "unknown"
    is_unknown: bool  # True если объект не распознан
    category: str | None  # Топ-1 категория
    confidence: float | None  # Уверенность топ-1 (0.0 - 1.0)
    top_k: list[TopPrediction]  # Топ-3 предсказания
    mock: bool = False  # True если ML Service недоступен


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: list[ErrorDetail] | None = None
