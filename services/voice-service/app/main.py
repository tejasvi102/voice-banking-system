import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from app.api.v1.endpoints import biometric, voice_command
from app.models import voice_profile
from app.db.migrations.session import Base, engine
from sqlalchemy.exc import SQLAlchemyError



# Load environment variables
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Voice Service")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8003))
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true"

logger = logging.getLogger(__name__)


# ✅ Proper lifespan handler (THIS IS THE FIX)
@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting up Voice Service...")

    # Create tables if enabled
    if AUTO_CREATE_TABLES:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ensured.")
        except SQLAlchemyError:
            logger.exception("Failed to auto-create database tables.")
            raise

    # ✅ LOAD MODELS HERE (blocking, guaranteed)
    logger.info("Intent service ready (no local model to load).")

    logger.info("Startup complete. API ready.")

    yield

    logger.info("Shutting down Voice Service...")


# Create FastAPI app with lifespan
app = FastAPI(
    title=APP_NAME,
    lifespan=lifespan
)


# ❌ REMOVE this completely (do not use on_event)
# @app.on_event("startup")
# async def startup_event():
#     load_stt()
#     load_intent()


# Routers
app.include_router(
    biometric.router,
    prefix="/voice/biometric",
    tags=["Biometric"]
)

app.include_router(
    voice_command.router,
    prefix="/voice/command",
    tags=["Voice Command"]
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
        "app.main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=False
    )
