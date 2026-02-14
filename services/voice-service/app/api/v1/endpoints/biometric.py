from fastapi import APIRouter, File, HTTPException, UploadFile
from app.core.vector_db import collection
from app.services import biometric_service


router = APIRouter()


@router.post("/register")
async def register_voice(user_id: str, file: UploadFile = File(...)):
    print("All IDs in DB:",collection.get()["ids"])
    print("Total count:", collection.count())
    return await biometric_service.register_voice(user_id, file)


@router.post("/verify")
async def verify_voice(user_id: str, file: UploadFile = File(...)):
    try:
        return await biometric_service.verify_voice(user_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
