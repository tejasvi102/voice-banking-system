import os
import requests
from app.services import stt_service, intent_service
from app.services.response_service import generate_response
import httpx
from fastapi import HTTPException
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8007")



async def resolve_recipient(user_id: str, recipient_name: str):

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/api/v1/users/resolve",
                params={
                    "name": recipient_name,
                    "requester_id": user_id
                }
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="User service unavailable"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="User service error"
        )

    data = response.json()

    if "error" in data and data["error"] == "multiple_users_found":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "MULTIPLE_RECIPIENTS",
                "matches": data["matches"]
            }
        )

    return data["user_id"]


async def process_voice_request(user_id, file):

    try:
        stt_result = await stt_service.transcribe(file)
        transcription = stt_result["text"]
        language = stt_result["language"]

        intent_data = await intent_service.detect_intent_and_entities(transcription)

        intent = intent_data["intent"]
        amount = intent_data.get("amount")
        recipient_name = intent_data.get("recipient")

        recipient_user_id = None

        if intent == "transfer_money":
            if not amount:
                raise HTTPException(
                    status_code=400,
                    detail="Transfer amount missing"
                )

            if not recipient_name:
                raise HTTPException(
                    status_code=400,
                    detail="Recipient missing"
                )

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

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Voice processing failed"
        )