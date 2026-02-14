import os
import asyncio
import numpy as np
from fastapi import HTTPException

from app.repositories.voice_repository import (
    get_user_embedding,
    save_voice_embedding,
)
from app.services.embedding_service import (
    extract_embedding as extract_upload_embedding,
)

THRESHOLD = 0.80


# -------------------------------
# Cosine Similarity
# -------------------------------
def compute_similarity(embedding1, embedding2) -> float:
    vec1 = np.asarray(embedding1, dtype=np.float32).flatten()
    vec2 = np.asarray(embedding2, dtype=np.float32).flatten()

    denominator = np.linalg.norm(vec1) * np.linalg.norm(vec2)

    if denominator == 0:
        return 0.0

    similarity = np.dot(vec1, vec2) / denominator

    return float(similarity)   # 🔥 ensures no ambiguous numpy truth error


# -------------------------------
# Register Voice
# -------------------------------
async def register_voice(user_id: str, file):
    embedding = await extract_upload_embedding(file)

    await save_voice_embedding(user_id, embedding)

    return {"status": "registered"}


# -------------------------------
# Verify Voice
# -------------------------------
async def verify_voice(user_id: str, file):
    new_embedding = await extract_upload_embedding(file)

    stored_embedding = await get_user_embedding(user_id)

    if stored_embedding is None:
        raise HTTPException(
            status_code=404,
            detail="Voice profile not found",
        )

    similarity = compute_similarity(new_embedding, stored_embedding)

    return {
        "verified": bool(similarity > THRESHOLD),
        "score": similarity,
    }


# -------------------------------
# File-path based embedding helper
# (used for enroll/verify from file path endpoints)
# -------------------------------
def extract_embedding(file_path: str):
    class _PathUploadFile:
        def __init__(self, path: str):
            self._path = path
            self.filename = os.path.basename(path)

        async def read(self):
            with open(self._path, "rb") as f:
                return f.read()

    async def _extract():
        return await extract_upload_embedding(_PathUploadFile(file_path))

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import threading

        result_holder = {}
        error_holder = {}

        def _worker():
            try:
                result_holder["value"] = asyncio.run(_extract())
            except Exception as exc:
                error_holder["error"] = exc

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        thread.join()

        if "error" in error_holder:
            raise error_holder["error"]

        return result_holder["value"]

    return asyncio.run(_extract())
