from pydantic import BaseModel, EmailStr
from uuid import UUID


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
    access_token: str
    refresh_token: str
    token_type: str
