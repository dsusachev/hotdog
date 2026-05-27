from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
