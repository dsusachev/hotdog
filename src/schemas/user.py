from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


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
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
