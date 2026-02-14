from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.migrations.session import get_db
from app.models.voice_profile import VoiceProfile
from app.services.biometric_service import extract_embedding, verify_voice as verify_voice_embedding
import uuid
import os

router = APIRouter()

@router.post("/enroll")
async def enroll_voice(
    user_id: uuid.UUID,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = f"temp_{audio.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())

    embedding = extract_embedding(file_path)
    os.remove(file_path)

    voice_profile = VoiceProfile(
        user_id=user_id,
        embedding=embedding.tolist()
    )

    try:
        db.add(voice_profile)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while saving voice profile")

    return {"message": "Voice enrolled successfully"}


@router.post("/verify")
async def verify_voice(
    user_id: uuid.UUID,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = f"temp_{audio.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())

    new_embedding = extract_embedding(file_path)
    os.remove(file_path)

    try:
        verified, similarity = verify_voice_embedding(db, user_id, new_embedding)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while verifying voice profile")

    return {
        "verified": verified,
        "similarity": similarity
    }
