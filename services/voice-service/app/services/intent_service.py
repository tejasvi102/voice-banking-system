import os
import json
import re
from groq import Groq
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False
from fastapi import HTTPException

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Llama 3 8B model on Groq was deprecated; use current replacement by default.
MODEL_ID = os.getenv("GROQ_INTENT_MODEL", "llama-3.1-8b-instant")


def _extract_json_payload(raw_content: str) -> dict:
    content = (raw_content or "").strip()
    if not content:
        raise HTTPException(status_code=502, detail="Intent model returned an empty response")

    # Accept both plain JSON and fenced markdown JSON blocks.
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.DOTALL)
    if fenced_match:
        content = fenced_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if brace_match:
            content = brace_match.group(0)

    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Intent model returned invalid JSON")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Intent model returned unexpected payload")

    payload.setdefault("intent", "other")
    payload.setdefault("amount", None)
    payload.setdefault("recipient", None)
    return payload


async def detect_intent_and_entities(text):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured")

    prompt = f"""
Extract banking intent and entities.

Command: "{text}"

Return ONLY JSON:

{{
  "intent": "balance_check | transfer_money | transaction_history | other",
  "amount": number or null,
  "recipient": name or upi_id or null
}}
"""

    try:
        response = client.chat.completions.create(

            model=MODEL_ID,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0,
        )
    except Exception:
        raise HTTPException(status_code=503, detail="Intent service unavailable")

    result = response.choices[0].message.content

    return _extract_json_payload(result)
