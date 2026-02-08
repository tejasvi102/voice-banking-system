from sqlalchemy.orm import Session
from app.models.user import User

def create_user(
    db: Session,
    auth_user_id,
    email: str,
    full_name: str | None,
    phone: str | None,
):
    existing = (
        db.query(User)
        .filter(User.auth_user_id == auth_user_id)
        .first()
    )
    if existing:
        return existing

    user = User(
        auth_user_id=auth_user_id,
        email=email,
        full_name=full_name,
        phone=phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_auth_id(db: Session, auth_user_id):
    return (
        db.query(User)
        .filter(User.auth_user_id == auth_user_id)
        .first()
    )
