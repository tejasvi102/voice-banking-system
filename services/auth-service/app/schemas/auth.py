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
    # phone: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
=======
    # phone: int
>>>>>>> d90f000 (feat: implement JWT authentication and token verification in auth service)

class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
=======
    # phone: int
    # full_name: str
>>>>>>> d90f000 (feat: implement JWT authentication and token verification in auth service)
