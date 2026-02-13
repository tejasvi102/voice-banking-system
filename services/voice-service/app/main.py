import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from app.api.v1.endpoints import biometric
from app.models import voice_profile
from app.db.migrations.session import Base, engine
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8003))
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true"


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if AUTO_CREATE_TABLES:
        try:
            Base.metadata.create_all(bind=engine)
        except SQLAlchemyError:
            logger.exception("Failed to auto-create database tables.")
            raise
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)

app.include_router(
    biometric.router,
    prefix="/voice/biometric",
    tags=["Biometric"]
)

@app.get("/health")
def health():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=APP_PORT
    )
