import os
import logging
from contextlib import asynccontextmanager
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import biometric, voice_command, voice
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

app.include_router(
    voice.router,
    prefix="/voice/profile",
    tags=["Voice Profile"]
)

@app.get("/health")
def health():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=False
    )
