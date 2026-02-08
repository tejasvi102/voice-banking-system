import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

# Load .env
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV")
APP_PORT = int(os.getenv("APP_PORT", 8000))

app = FastAPI(title=APP_NAME)

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
