from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.deps import get_db
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user_service import create_user, get_user_by_auth_id
from app.core.auth import get_current_auth_user
# from app.core.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
def create_user_profile(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(get_current_auth_user),
):
    auth_user_id = auth_payload["sub"]

    user = create_user(
        db=db,
        auth_user_id=auth_user_id,
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
    )
    return user


@router.get("/me", response_model=UserResponse)
def get_me(
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(get_current_auth_user),
):
    auth_user_id = auth_payload.get("sub")

    user = get_user_by_auth_id(db, auth_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
