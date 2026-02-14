import torch
import torchaudio
import numpy as np
import soundfile as sf
import inspect
import huggingface_hub
from app.models.voice_profile import VoiceProfile

# ✅ Force torchaudio to use soundfile backend (avoid TorchCodec issues on Windows)
try:
    torchaudio.set_audio_backend("soundfile")
except Exception:
    pass

# Compatibility fix for newer torchaudio versions
if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: ["soundfile"]

_classifier = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        # speechbrain 1.0.x may pass use_auth_token, removed in huggingface_hub 1.x.
        if "use_auth_token" not in inspect.signature(huggingface_hub.hf_hub_download).parameters:
            _orig_hf_hub_download = huggingface_hub.hf_hub_download

            def _hf_hub_download_compat(*args, use_auth_token=None, **kwargs):
                if use_auth_token is not None and "token" not in kwargs:
                    kwargs["token"] = use_auth_token
                return _orig_hf_hub_download(*args, **kwargs)

            huggingface_hub.hf_hub_download = _hf_hub_download_compat

        from speechbrain.inference.classifiers import EncoderClassifier

        _classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/ecapa"
        )
    return _classifier


def extract_embedding_from_file(file_path: str):
    # Use soundfile to avoid torchaudio's TorchCodec dependency on Windows.
    signal_np, fs = sf.read(file_path, always_2d=True, dtype="float32")
    signal_np = np.mean(signal_np, axis=1)
    signal = torch.from_numpy(signal_np).unsqueeze(0)

    # ECAPA model expects 16kHz audio.
    if fs != 16000:
        signal = torchaudio.functional.resample(signal, fs, 16000)

    classifier = _get_classifier()

    # SpeechBrain expects shape: [batch, time]
    embedding = classifier.encode_batch(signal)

    embedding = embedding.squeeze().detach().cpu().numpy()

    # ✅ Normalize embedding (important for cosine similarity)
    embedding = embedding / np.linalg.norm(embedding)

    return embedding


def extract_embedding(file_path: str):
    return extract_embedding_from_file(file_path)


def verify_voice(db, user_id, incoming_embedding):
    profile = db.query(VoiceProfile).filter_by(user_id=user_id).first()
    if profile is None:
        return False, 0.0

    stored_embedding = np.asarray(profile.embedding, dtype=np.float32)
    incoming_embedding = np.asarray(incoming_embedding, dtype=np.float32)

    denominator = np.linalg.norm(stored_embedding) * np.linalg.norm(incoming_embedding)
    if denominator == 0:
        return False, 0.0

    similarity = float(np.dot(stored_embedding, incoming_embedding) / denominator)
    threshold = 0.80  # You can tune later

    return similarity >= threshold, similarity
