from sqlalchemy.orm import Session
from app.models.user import User


def create_user(
    db: Session,
    auth_user_id,
    email: str,
    full_name: str | None,
    phone: str | None,
):
    user = db.query(User).filter(User.id == auth_user_id).first()
    if not user:
        raise ValueError("User not found")

    if email:
        user.email = email
    user.full_name = full_name
    user.phone = phone

    db.commit()
    db.refresh(user)
    return user


def get_user_by_auth_id(db: Session, auth_user_id):
    return (
        db.query(User)
        .filter(User.id == auth_user_id)
        .first()
    )
