import requests
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

AUTH_VERIFY_URL = "http://localhost:8001/auth/verify"

def get_current_auth_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    response = requests.get(
        AUTH_VERIFY_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return response.json()
