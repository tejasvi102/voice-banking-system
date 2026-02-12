import os
import sys
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.db.migrations.session import engine
from app.db.migrations.base import Base
from app.db.migrations.bootstrap import ensure_user_columns

# Load environment variables
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8007))

app = FastAPI(title=APP_NAME)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_user_columns()


@app.get("/health")
def health():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=APP_ENV == "development",
    )

app.include_router(auth_router)
app.include_router(users_router, prefix="/api/v1")
