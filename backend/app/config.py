import os
from pathlib import Path

MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/app/models"))

PIPER_VOICES = {
    "id": {
        "model": MODELS_DIR / "piper" / "id_ID-news_tts-medium.onnx",
        "config": MODELS_DIR / "piper" / "id_ID-news_tts-medium.onnx.json",
    },
    "en": {
        "model": MODELS_DIR / "piper" / "en_US-lessac-medium.onnx",
        "config": MODELS_DIR / "piper" / "en_US-lessac-medium.onnx.json",
    },
}

# Your trained RVC speaker model (see voice_training/RVC_TRAINING_GUIDE.md).
# Drop the two files produced by training here with these exact names,
# or override the paths via env vars.
RVC_MODEL_PATH = Path(os.environ.get("RVC_MODEL_PATH", MODELS_DIR / "rvc" / "my_voice.pth"))
RVC_INDEX_PATH = Path(os.environ.get("RVC_INDEX_PATH", MODELS_DIR / "rvc" / "my_voice.index"))

# Pitch shift (semitones) applied during voice conversion. 0 usually works
# when your reference recordings and the target text are spoken register are
# similar. Tweak per docs/ARCHITECTURE.md if the output sounds off-pitch.
RVC_PITCH_SHIFT = int(os.environ.get("RVC_PITCH_SHIFT", "0"))

# Where Applio (the voice conversion engine) was cloned to in the Docker
# image -- see backend/Dockerfile. Its core.py is invoked as a subprocess.
APPLIO_DIR = Path(os.environ.get("APPLIO_DIR", "/app/applio"))
RVC_INDEX_RATE = float(os.environ.get("RVC_INDEX_RATE", "0.5"))
RVC_PROTECT = float(os.environ.get("RVC_PROTECT", "0.33"))
RVC_F0_METHOD = os.environ.get("RVC_F0_METHOD", "rmvpe")

MAX_TEXT_LENGTH = int(os.environ.get("MAX_TEXT_LENGTH", "1000"))
