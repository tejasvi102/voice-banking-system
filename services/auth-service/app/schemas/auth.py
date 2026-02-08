from pydantic import BaseModel, EmailStr
from uuid import UUID


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
    # phone: int
    # full_name: str
