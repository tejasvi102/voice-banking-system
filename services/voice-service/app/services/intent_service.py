import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Llama 3 8B model on Groq was deprecated; use current replacement by default.
MODEL_ID = os.getenv("GROQ_INTENT_MODEL", "llama-3.1-8b-instant")


async def detect_intent_and_entities(text):

    prompt = f"""
Extract banking intent and entities.

Command: "{text}"

Return ONLY JSON:

{{
  "intent": "balance_check | transfer_money | transaction_history | other",
  "amount": number or null,
  "recipient": string or null
}}
"""

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

    result = response.choices[0].message.content

    return json.loads(result)
