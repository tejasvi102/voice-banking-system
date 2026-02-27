import os
import json
import urllib.error
import urllib.parse
import urllib.request
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import uvicorn

# Load environment variables
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8000))
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://localhost:8003")

app = FastAPI(title=APP_NAME)


@app.get("/health")
def health():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP"
    }


@app.post("/voice/command/confirm-transfer")
def confirm_transfer_proxy(user_id: str, payload: dict):
    query = urllib.parse.urlencode({"user_id": user_id})
    target_url = f"{VOICE_SERVICE_URL}/voice/command/confirm-transfer?{query}"

    request = urllib.request.Request(
        url=target_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {"status": "ok"}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise HTTPException(
            status_code=exc.code,
            detail=detail or "Voice service request failed"
        )
    except urllib.error.URLError:
        raise HTTPException(status_code=503, detail="Voice service unavailable")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=APP_ENV == "development"
    )
