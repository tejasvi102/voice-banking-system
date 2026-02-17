from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.migrations.deps import get_db
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user_service import create_user, get_user_by_auth_id
from app.core.auth import get_current_auth_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/resolve")
def resolve_user(
    name: str = Query(...),
    requester_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Resolve recipient name to user_id
    """

    users = (
        db.query(User)
        .filter(User.full_name.ilike(f"{name}%"))
        .all()
    )

    if not users:
        raise HTTPException(
            status_code=404,
            detail="user_not_found"
        )

    if len(users) > 1:
        return {
            "error": "multiple_users_found",
            "matches": [user.full_name for user in users]
        }

    user = users[0]

    return {
        "user_id": str(user.id),
        "full_name": user.full_name
    }
@router.post("", response_model=UserResponse)
def create_user_profile(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(get_current_auth_user),
):
    auth_user_id = auth_payload["sub"]

    try:
        user = create_user(
            db=db,
            auth_user_id=auth_user_id,
            email=payload.email,
            full_name=payload.full_name,
            phone=payload.phone,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
