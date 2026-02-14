import torch
import torchaudio
import tempfile
import numpy as np
import inspect
import huggingface_hub
from huggingface_hub.errors import RemoteEntryNotFoundError
import librosa

_classifier = None
_device = "cuda" if torch.cuda.is_available() else "cpu"


def _prepare_compat() -> None:
    # SpeechBrain may call this on import; torchaudio 2.10 removed it.
    if not hasattr(torchaudio, "list_audio_backends"):
        torchaudio.list_audio_backends = lambda: ["soundfile"]

    # speechbrain 1.0.x passes use_auth_token, removed in huggingface_hub 1.x.
    if "use_auth_token" not in inspect.signature(huggingface_hub.hf_hub_download).parameters:
        original_download = huggingface_hub.hf_hub_download

        def hf_hub_download_compat(*args, use_auth_token=None, **kwargs):
            if use_auth_token is not None and "token" not in kwargs:
                kwargs["token"] = use_auth_token
            filename = kwargs.get("filename")
            if filename is None and len(args) >= 2:
                filename = args[1]
            try:
                return original_download(*args, **kwargs)
            except RemoteEntryNotFoundError:
                # Some SpeechBrain checkpoints do not ship custom.py.
                if filename == "custom.py":
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix="_custom.py", delete=False
                    ) as tmp:
                        tmp.write("# optional custom module placeholder\n")
                        return tmp.name
                raise

        huggingface_hub.hf_hub_download = hf_hub_download_compat


def _get_model():
    """
    Loads speaker recognition model only once.
    """
    global _classifier

    if _classifier is None:
        _prepare_compat()
        from speechbrain.inference.speaker import EncoderClassifier

        _classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec",
            run_opts={"device": _device}
        )

    return _classifier


async def extract_embedding(upload_file):
    """
    Takes FastAPI UploadFile and returns speaker embedding as numpy array
    """

    model = _get_model()

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await upload_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Load audio
    
    audio, fs = librosa.load(tmp_path, sr=16000)

    # Convert to tensor
    signal = torch.tensor(audio).unsqueeze(0).to(_device)

    # Ensure correct sample rate (SpeechBrain expects 16kHz)
    if fs != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=fs, new_freq=16000)
        signal = resampler(signal)

    # Move to device
    signal = signal.to(_device)

    with torch.no_grad():
        embedding = model.encode_batch(signal)

    # Convert to numpy
    embedding = embedding.squeeze().cpu().numpy()

    return embedding
