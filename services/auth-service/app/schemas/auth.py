from pydantic import BaseModel, EmailStr
<<<<<<< HEAD
<<<<<<< HEAD
from uuid import UUID

=======
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
from uuid import UUID

>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)

class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
<<<<<<< HEAD
=======
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
