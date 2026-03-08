from fastapi import APIRouter, UploadFile, File
from app.services.orchestrator import process_voice_request
from app.services.response_service import generate_response
from app.services.tts_service import synthesize

router = APIRouter()


@router.post("/voice-command")
async def voice_command(user_id: str, file: UploadFile = File(...)):

    # Step 1 → Process voice
    result = await process_voice_request(user_id, file)

    # Step 2 → Generate response text
    response_text = await generate_response(
        intent=result.get("intent"),
        data=result,
        language=result.get("language", "en")
    )

    # Step 3 → Convert to speech
    audio_path = await synthesize(
        text=response_text,
        language=result.get("language", "en")
    )

    return {
        "voice_response": response_text,
        "audio_file": audio_path,
        "pipeline_result": result
    }