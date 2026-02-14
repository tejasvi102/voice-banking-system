from app.services import stt_service, intent_service, biometric_service

async def process_transaction(user_id, file):
    text = await stt_service.transcribe(file)
    intent = await intent_service.detect(text)

    if intent in ["transfer", "withdraw"]:
        verification = await biometric_service.verify_voice(user_id, file)

        if not verification["verified"]:
            return {"status": "voice_failed"}

    return {"status": "success", "intent": intent}
