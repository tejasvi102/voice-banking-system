from fastapi import APIRouter, UploadFile, File
from app.services.orchestrator import process_voice_request

router = APIRouter()


@router.post("/process")
async def process_voice(user_id: str, file: UploadFile = File(...)):
    return await process_voice_request(user_id, file)
