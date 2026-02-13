from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.migrations.session import get_db
from app.models.voice_profile import VoiceProfile
from app.services.biometric_service import extract_embedding
from app.services.biometric_service import compute_similarity
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

    db.add(voice_profile)
    db.commit()

    return {"message": "Voice enrolled successfully"}


@router.post("/verify")
async def verify_voice(
    user_id: uuid.UUID,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    profile = db.query(VoiceProfile).filter_by(user_id=user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    file_path = f"temp_{audio.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())

    new_embedding = extract_embedding(file_path)
    os.remove(file_path)

    similarity = compute_similarity(profile.embedding, new_embedding)

    threshold = 0.80
    verified = similarity >= threshold

    return {
        "verified": verified,
        "similarity": similarity
    }
