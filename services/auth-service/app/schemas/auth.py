from pydantic import BaseModel, EmailStr
<<<<<<< HEAD
from uuid import UUID

=======
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
<<<<<<< HEAD

class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
=======
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
