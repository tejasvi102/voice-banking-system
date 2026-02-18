from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest, LoginRequest, RegisterResponse, RefreshTokenRequest
from app.services.auth_service import register_user, authenticate_user
from app.db.migrations.deps import get_db
from app.core.security import create_access_token, decode_access_token
from app.core.tokens import generate_refresh_token, refresh_expiry, hash_refresh_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])
http_bearer = HTTPBearer()


# ---------------- REGISTER ----------------
@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, payload.email, payload.password, payload.full_name)

        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
        )

        raw_refresh = generate_refresh_token()
        user.refresh_token_hash = hash_refresh_token(raw_refresh)
        user.refresh_token_expires_at = refresh_expiry()
        db.commit()

        return {
            "id": user.id,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------- LOGIN ----------------
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, payload.email, payload.password)

        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
        )

        raw_refresh = generate_refresh_token()
        user.refresh_token_hash = hash_refresh_token(raw_refresh)
        user.refresh_token_expires_at = refresh_expiry()
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


# ---------------- REFRESH ----------------
@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)

    user = (
        db.query(User)
        .filter(User.refresh_token_hash == token_hash)
        .first()
    )

    if not user or user.refresh_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # rotate
    new_raw = generate_refresh_token()
    user.refresh_token_hash = hash_refresh_token(new_raw)
    user.refresh_token_expires_at = refresh_expiry()

    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
    )

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_raw,
        "token_type": "bearer",
    }


# ---------------- LOGOUT ----------------
@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # revoke refresh token
    user.refresh_token_hash = None
    user.refresh_token_expires_at = None
    db.commit()

    return {"message": "Logged out successfully"}


# ---------------- VERIFY ----------------
@router.get("/verify")
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload
