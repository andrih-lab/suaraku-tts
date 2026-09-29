"""Thin wrapper around piper-tts: text -> base speech audio (generic voice,
natural prosody, correct language pronunciation). This stage does NOT sound
like you yet -- app/voice_convert.py handles that.
"""

import io
import wave
from pathlib import Path

from piper import PiperVoice

from . import config


class PiperEngine:
    def __init__(self) -> None:
        self._voices: dict[str, PiperVoice] = {}

    def loaded_languages(self) -> list[str]:
        return list(self._voices.keys())

    def load(self) -> None:
        for lang, paths in config.PIPER_VOICES.items():
            model_path: Path = paths["model"]
            config_path: Path = paths["config"]
            if not model_path.exists() or not config_path.exists():
                # Voice not installed yet -- skip rather than crash the whole
                # service. /api/health reports which languages are missing.
                continue
            self._voices[lang] = PiperVoice.load(str(model_path), config_path=str(config_path))

    def synthesize_to_wav_bytes(self, text: str, language: str) -> bytes:
        voice = self._voices.get(language)
        if voice is None:
            raise RuntimeError(
                f"No Piper voice loaded for language '{language}'. "
                "Check models/piper/ and MODELS_DIR (see README)."
            )

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        return buf.getvalue()


piper_engine = PiperEngine()
