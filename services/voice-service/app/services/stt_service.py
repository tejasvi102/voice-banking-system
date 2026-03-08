import os
import requests
import tempfile
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False
from langdetect import detect, LangDetectException
from fastapi import HTTPException


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Use HF router inference endpoint (legacy api-inference is deprecated).
MODEL_ID = "openai/whisper-large-v3"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}


async def transcribe(file):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    if not HF_TOKEN:
        raise HTTPException(status_code=500, detail="HF_TOKEN is not configured")

    with open(tmp_path, "rb") as f:
        audio_bytes = f.read()

    headers = dict(HEADERS)
    headers["Content-Type"] = file.content_type or "application/octet-stream"

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            data=audio_bytes,
            timeout=120
        )
    except requests.RequestException:
        os.remove(tmp_path)
        raise HTTPException(status_code=503, detail="Speech-to-text service unavailable")

    os.remove(tmp_path)

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Speech-to-text failed with status {response.status_code}"
        )

    result = response.json()

    text = result.get("text", "").strip()

    try:
        language = detect(text) if text else "unknown"
    except LangDetectException:
        language = "unknown"

    return {
        "text": text,
        "language": language
    }
