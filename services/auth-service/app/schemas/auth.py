from pydantic import BaseModel, EmailStr
from uuid import UUID

class RefreshTokenRequest(BaseModel):
    refresh_token:str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    # phone: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    # phone: int

class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
    access_token: str
    refresh_token: str
    token_type: str
    # phone: int
    # full_name: str
