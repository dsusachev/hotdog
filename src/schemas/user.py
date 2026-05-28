from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateRequest(BaseModel):
    """Схема для регистрации нового пользователя"""
    email: EmailStr
    password: str
    display_name: str

class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: str
    email: EmailStr
    display_name: str | None
    is_active: bool

    from pydantic import field_validator
    @field_validator('id', mode='before')
    @classmethod
    def uuid_to_str(cls, v):
        return str(v)

    class Config:
        from_attributes = True  # Для работы с SQLAlchemy моделями (ранее orm_mode)

class UserLoginRequest(BaseModel):
    """Схема для логина"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    access_token: str
    token_type: str
