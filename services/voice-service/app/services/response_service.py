import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_ID = os.getenv("GROQ_RESPONSE_MODEL", "llama-3.1-8b-instant")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}


# Map ISO codes → full language names
LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
}


async def generate_response(intent, data, language):

    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set.")

    # Convert language code to readable language
    language_name = LANGUAGE_MAP.get(language, "English")

    prompt = f"""
You are a multilingual banking response generator.

IMPORTANT RULES:
1. Respond strictly in {language_name}.
2. Do NOT mix languages.
3. Do NOT transliterate.
4. Use natural native script only.
5. Do NOT add extra services or explanations.
6. Use ONLY the given data.
7. Keep response short and clear.

Intent: {intent}
Data: {data}

If intent is:
- balance_check → Inform user of their balance clearly.
- transfer_money → Confirm transfer amount and recipient.
- missing_information → Ask politely for missing details.

Generate the final response now.
"""

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": "You are a secure banking assistant that strictly follows instructions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 120
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            GROQ_URL,
            headers=HEADERS,
            json=payload
        )

    if response.status_code != 200:
        raise Exception(f"Groq error {response.status_code}: {response.text}")

    result = response.json()

    choices = result.get("choices")
    if not choices:
        raise Exception(f"Groq response missing choices: {result}")

    return choices[0]["message"]["content"].strip()
