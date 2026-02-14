import chromadb
from chromadb.config import Settings

client = chromadb.Client(
    Settings(
        persist_directory="./chroma_db",
        is_persistent=True
    )
)

collection = client.get_or_create_collection("voice_embeddings")
