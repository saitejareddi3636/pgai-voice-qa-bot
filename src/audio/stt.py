from pathlib import Path
from faster_whisper import WhisperModel


def transcribe_file(wav_path: Path, model_size: str = "base") -> str:
    model = WhisperModel(model_size)
    segments, _ = model.transcribe(str(wav_path))
    text = " ".join(s.text.strip() for s in segments).strip()
    return text