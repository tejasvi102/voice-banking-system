import torch
import librosa
import tempfile
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

MODEL_ID = "ai4bharat/indic-whisper-small"

_processor = None
_model = None

def _load_model():
    global _processor, _model

    if _processor is None or _model is None:
        _processor = AutoProcessor.from_pretrained(MODEL_ID)
        _model = AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_ID)
        _model.eval()

    return _processor, _model


async def transcribe(file):
    """
    Takes UploadFile and returns transcribed text
    """

    processor, model = _load_model()

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Load audio
    audio, sr = librosa.load(tmp_path, sr=16000)

    inputs = processor(audio, sampling_rate=16000, return_tensors="pt")

    with torch.no_grad():
        generated_ids = model.generate(**inputs)

    transcription = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    return transcription
