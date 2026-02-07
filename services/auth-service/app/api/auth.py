from fastapi import APIRouter, HTTPException, Depends
<<<<<<< HEAD
<<<<<<< HEAD
from app.schemas.auth import RegisterRequest, LoginRequest, RegisterResponse
=======
from app.schemas.auth import RegisterRequest, LoginRequest
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
from app.schemas.auth import RegisterRequest, LoginRequest, RegisterResponse
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
from app.services.auth_service import register_user, login_user
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.core.auth import get_current_user

router = APIRouter()


<<<<<<< HEAD
<<<<<<< HEAD
@router.post("/register", response_model=RegisterResponse)
=======
@router.post("/register")
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
@router.post("/register", response_model=RegisterResponse)
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, payload.email, payload.password)
        return {"id": user.id, "email": user.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = login_user(db, payload.email, payload.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.get("/verify")
def verify_token(payload: dict = Depends(get_current_user)):
    return {
        "valid": True,
        "email": payload.get("sub")
    }    