from fastapi import APIRouter, UploadFile, File, Body
from app.services.orchestrator import process_voice_request, confirm_transfer


router = APIRouter()


@router.post("/process")
async def process_voice(user_id: str, file: UploadFile = File(...)):
    return await process_voice_request(user_id, file)

@router.post("/confirm-transfer")
async def confirm_voice_transfer(
    user_id: str,
    recipient_user_id: str = Body(...),
    amount: float = Body(...)
):
    return await confirm_transfer(
        user_id=user_id,
        recipient_user_id=recipient_user_id,
        amount=amount
    )