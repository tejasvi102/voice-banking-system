from gtts import gTTS
import tempfile
import os


async def synthesize(text: str, language: str):

    tts = gTTS(text=text, lang=language)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    path = tmp.name

    tts.save(path)

    return path