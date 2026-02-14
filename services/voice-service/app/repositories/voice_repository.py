from app.core.vector_db import collection

async def save_voice_embedding(user_id, embedding):
    collection.upsert(
        ids=[str(user_id)],
        embeddings=[embedding.tolist()]
    )

async def get_user_embedding(user_id):
    result = collection.get(
        ids=[str(user_id)],
        include=["embeddings"]
    )

    embeddings = result.get("embeddings")

    # 🔥 FIX: Check length explicitly
    if embeddings is None or len(embeddings) == 0:
        return None

    return embeddings[0]
