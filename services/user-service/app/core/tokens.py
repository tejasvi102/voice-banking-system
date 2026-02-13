import uuid
from datetime import datetime, timedelta, timezone
import hashlib
from app.core.config import settings


def generate_refresh_token() -> str:
    return str(uuid.uuid4())


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def refresh_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_expire_days
    )
