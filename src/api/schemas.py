from pydantic import BaseModel, EmailStr


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


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None


class UserRegisterResponse(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    message: str = "Регистрация прошла успешно"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeResponse(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    is_active: bool
