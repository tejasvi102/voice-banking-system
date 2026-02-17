import os
import requests
from app.services import stt_service, intent_service

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8007")


async def resolve_recipient(user_id: str, recipient_name: str):

    response = requests.get(
        f"{USER_SERVICE_URL}/api/v1/users/resolve",
        params={
            "name": recipient_name,
            "requester_id": user_id
        }
    )

    if response.status_code == 404:
        raise Exception("Recipient not found")

    data = response.json()

    if "error" in data:

        if data["error"] == "multiple_users_found":
            raise Exception(
                f"Multiple users found: {data['matches']}"
            )

    return data["user_id"]


async def process_voice_request(user_id, file):

    stt_result = await stt_service.transcribe(file)

    transcription = stt_result["text"]
    language = stt_result["language"]

    intent_data = await intent_service.detect_intent_and_entities(
        transcription
    )

    intent = intent_data["intent"]
    amount = intent_data.get("amount")
    recipient_name = intent_data.get("recipient")

    recipient_user_id = None

    if intent == "transfer_money":

        recipient_user_id = await resolve_recipient(
            user_id,
            recipient_name
        )

    return {
        "status": "approved",
        "transcription": transcription,
        "intent": intent,
        "amount": amount,
        "recipient_user_id": recipient_user_id,
        "language": language
    }
