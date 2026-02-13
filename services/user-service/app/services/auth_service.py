import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("User already exists")

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        auth_user_id=user_id,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    return user
