"""Voice-conversion adapter: takes Piper's generic-voice audio and recolors
its timbre to match your cloned voice, using an RVC model trained from your
own recordings (see voice_training/RVC_TRAINING_GUIDE.md).

This shells out to Applio's `core.py infer` CLI (Applio is a maintained RVC
fork, cloned + installed in backend/Dockerfile) rather than importing its
internal Python modules. The CLI's flags are Applio's documented, stable
interface; internal module layout is not. If Applio's CLI flags change in a
future version you upgrade to, this is the only file that should need
updating -- main.py and tts_piper.py never call into Applio directly.
"""

import subprocess
import tempfile
from pathlib import Path

from . import config


class VoiceConverter:
    def is_ready(self) -> bool:
        return config.RVC_MODEL_PATH.exists() and config.RVC_INDEX_PATH.exists()

    def load(self) -> None:
        # Nothing to warm up -- each conversion runs as its own subprocess.
        pass

    def convert(self, wav_bytes: bytes) -> bytes:
        if not self.is_ready():
            # Pass audio through unchanged if no voice model is loaded yet.
            return wav_bytes

        with tempfile.TemporaryDirectory() as tmp_dir:
            in_path = Path(tmp_dir) / "piper_out.wav"
            out_path = Path(tmp_dir) / "converted.wav"
            in_path.write_bytes(wav_bytes)

            result = subprocess.run(
                [
                    "python3",
                    "core.py",
                    "infer",
                    "--input-path",
                    str(in_path),
                    "--output-path",
                    str(out_path),
                    "--pth-path",
                    str(config.RVC_MODEL_PATH),
                    "--index-path",
                    str(config.RVC_INDEX_PATH),
                    "--pitch",
                    str(config.RVC_PITCH_SHIFT),
                    "--f0-method",
                    config.RVC_F0_METHOD,
                    "--index-rate",
                    str(config.RVC_INDEX_RATE),
                    "--protect",
                    str(config.RVC_PROTECT),
                ],
                cwd=str(config.APPLIO_DIR),
                capture_output=True,
                text=True,
                # Generous: on CPU, each call re-loads HuBERT/RMVPE/the RVC
                # model from disk from scratch (no caching between
                # requests) -- see docs/ARCHITECTURE.md.
                timeout=300,
            )

            if result.returncode != 0 or not out_path.exists():
                raise RuntimeError(
                    f"Applio inference failed (exit {result.returncode}): "
                    f"{result.stderr[-2000:]}"
                )

            return out_path.read_bytes()


voice_converter = VoiceConverter()
