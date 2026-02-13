import torch
import torchaudio
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.voice_profile import VoiceProfile
from sqlalchemy import select

# torchaudio 2.10 removed list_audio_backends, but current SpeechBrain still calls it.
if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: ["soundfile"]

_classifier = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        from speechbrain.inference.classifiers import EncoderClassifier

        _classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/ecapa"
        )
    return _classifier

def extract_embedding_from_file(file_path: str):
    signal, fs = torchaudio.load(file_path)

    # Convert to mono if stereo
    if signal.shape[0] > 1:
        signal = torch.mean(signal, dim=0, keepdim=True)

    classifier = _get_classifier()
    embedding = classifier.encode_batch(signal)
    embedding = embedding.squeeze().detach().numpy()

    # Normalize embedding (important for cosine similarity)
    embedding = embedding / np.linalg.norm(embedding)

    return embedding


def extract_embedding(file_path: str):
    return extract_embedding_from_file(file_path)

def compute_similarity(embedding1, embedding2):
    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]
    return float(similarity)


def verify_voice(db, user_id, incoming_embedding):
    result = db.execute(
        select(
            1 - VoiceProfile.embedding.cosine_distance(incoming_embedding)
        ).where(VoiceProfile.user_id == user_id)
    ).scalar()

    if result is None:
        return False, 0.0

    similarity = float(result)
    threshold = 0.80

    return similarity >= threshold, similarity
