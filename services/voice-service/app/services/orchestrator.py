import os
import uuid
import httpx
from fastapi import HTTPException
from app.services import stt_service, intent_service

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8007")
BANKING_CORE_URL = os.getenv("BANKING_CORE_URL", "http://localhost:8002")


# ----------------------------
# Resolve Recipient
# ----------------------------
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
        raise HTTPException(404, "Recipient not found")

    if response.status_code != 200:
        raise HTTPException(500, "User service error")

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


# ----------------------------
# Voice Processing (Step 1)
# ----------------------------
async def process_voice_request(user_id, file):

    try:
        stt_result = await stt_service.transcribe(file)
        transcription = stt_result.get("text", "").strip()
        language = stt_result["language"]
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")

        intent_data = await intent_service.detect_intent_and_entities(transcription)

        intent = intent_data.get("intent", "other")
        amount = intent_data.get("amount")
        recipient_name = intent_data.get("recipient")

        if intent == "transfer_money":

            if not amount:
                raise HTTPException(400, "Transfer amount missing")

            if not recipient_name:
                raise HTTPException(400, "Recipient missing")

            recipient_user_id = await resolve_recipient(user_id, recipient_name)

            # 🔥 Return pending confirmation instead of executing transfer
            return {
                "status": "pending_confirmation",
                "transcription": transcription,
                "intent": intent,
                "amount": amount,
                "recipient_name": recipient_name,
                "recipient_user_id": recipient_user_id,
                "language": language
            }

        # For non-transfer intents
        return {
            "status": "approved",
            "transcription": transcription,
            "intent": intent,
            "amount": amount,
            "recipient_user_id": None,
            "language": language
        }

    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(500, "Voice processing failed")


# ----------------------------
# Transfer Confirmation (Step 2)
# ----------------------------
async def confirm_transfer(user_id: str, recipient_user_id: str, amount: float):

    idempotency_key = str(uuid.uuid4())

    payload = {
        "from_user_id": user_id,
        "to_user_id": recipient_user_id,
        "amount": amount,
        "currency": "INR",
        "idempotency_key": idempotency_key
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                f"{BANKING_CORE_URL}/transfers/execute",
                json=payload
            )
    except httpx.RequestError:
        raise HTTPException(503, "Banking core unavailable")

    if response.status_code != 200:
        detail = "Transfer failed"
        try:
            response_payload = response.json()
            detail = response_payload.get("detail") or detail
        except Exception:
            pass
        raise HTTPException(response.status_code, detail)

    return {
        "status": "success",
        "message": "Transfer completed successfully",
        "idempotency_key": idempotency_key,
        "transaction_data": response.json()
    }
