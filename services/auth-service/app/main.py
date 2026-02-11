import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> d90f000 (feat: implement JWT authentication and token verification in auth service)

from app.api.auth import router as auth_router
from app.db.migrations.bootstrap import ensure_refresh_token_columns

import uvicorn


from app.api.auth import router as auth_router
<<<<<<< HEAD
# >>>>>>> Stashed changes
>>>>>>> main
=======
from flask import app
import uvicorn
=======

>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
from app.api.auth import router as auth_router
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
>>>>>>> d90f000 (feat: implement JWT authentication and token verification in auth service)

# Load .env
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV")
APP_PORT = int(os.getenv("APP_PORT", 8000))

app = FastAPI(title=APP_NAME)

@app.on_event("startup")
def startup() -> None:
    ensure_refresh_token_columns()

@app.get("/auth")
def auth():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=APP_ENV == "development"
    )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
# <<<<<<< Updated upstream
# =======
>>>>>>> main
=======
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
>>>>>>> d90f000 (feat: implement JWT authentication and token verification in auth service)

@app.get("/")
def health():
    return {"status": "auth-service UP"}

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
<<<<<<< HEAD
<<<<<<< HEAD
=======
# <<<<<<< Updated upstream
# >>>>>>> Stashed changes
# =======
# >>>>>>> Stashed changes
>>>>>>> main
=======
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
=======
=======
app.include_router(auth_router)
>>>>>>> 6e5649f (VB-04: Complete Auth system with refresh rotation, logout, hashing + user service integration)

>>>>>>> d90f000 (feat: implement JWT authentication and token verification in auth service)
