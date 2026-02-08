from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    auth_user_id: UUID
    email: EmailStr
    full_name: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True
