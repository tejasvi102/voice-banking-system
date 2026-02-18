import os
import requests
import tempfile
from dotenv import load_dotenv
from langdetect import detect, LangDetectException


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
        raise Exception("HF_TOKEN is not set. Set it in your environment or .env.")

    with open(tmp_path, "rb") as f:
        audio_bytes = f.read()

    headers = dict(HEADERS)
    headers["Content-Type"] = "audio/wav"

    response = requests.post(
        API_URL,
        headers=headers,
        data=audio_bytes,
        timeout=120
    )

    os.remove(tmp_path)

    if response.status_code != 200:
        raise Exception(f"HF inference error {response.status_code}: {response.text}")

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