import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

# Load environment variables
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8003))

app = FastAPI(title=APP_NAME)


@app.get("/health")
def health():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=APP_ENV == "development"
    )
