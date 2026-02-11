import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI


from app.api.auth import router as auth_router
from app.db.migrations.bootstrap import ensure_refresh_token_columns

import uvicorn


from app.api.auth import router as auth_router

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

@app.get("/")
def health():
    return {"status": "auth-service UP"}

app.include_router(auth_router)

