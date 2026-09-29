"""Voice-conversion adapter: takes Piper's generic-voice audio and recolors
its timbre to match your cloned voice, using an RVC model trained from your
own recordings (see voice_training/RVC_TRAINING_GUIDE.md).

WHY THIS FILE IS ISOLATED
RVC inference libraries on PyPI change their call signatures fairly often.
Every other module in this backend talks to `converter.convert(...)` only --
never to the underlying library directly. If `rvc-python`'s API has moved
since this was written, this is the ONLY file you should need to touch: run
`pip show rvc-python` and check its current source for the loader +
inference call, then update `load` and `convert` below to match.

The calls used here (`RVCInference(device=...)`, `load_model(path,
index_path=..., version=...)`, `set_params(**kwargs)`, `infer_file(in, out)`)
match rvc-python's rvc_python/infer.py as published by daswer123.
"""

import tempfile
from pathlib import Path

from . import config


class VoiceConverter:
    def __init__(self) -> None:
        self._model = None
        self._ready = False

    def is_ready(self) -> bool:
        return self._ready

    def load(self) -> None:
        if not config.RVC_MODEL_PATH.exists() or not config.RVC_INDEX_PATH.exists():
            # No trained voice yet -- server still runs, serving Piper's
            # generic voice until you drop your trained model in place.
            return

        from rvc_python.infer import RVCInference  # local import: heavy, optional

        self._model = RVCInference(device="cpu:0")
        self._model.load_model(
            str(config.RVC_MODEL_PATH),
            index_path=str(config.RVC_INDEX_PATH),
            version="v2",
        )
        self._model.set_params(
            f0up_key=config.RVC_PITCH_SHIFT,
            f0method="harvest",
            index_rate=0.5,
            protect=0.33,
        )
        self._ready = True

    def convert(self, wav_bytes: bytes) -> bytes:
        if not self._ready or self._model is None:
            # Pass audio through unchanged if no voice model is loaded yet.
            return wav_bytes

        with tempfile.TemporaryDirectory() as tmp_dir:
            in_path = Path(tmp_dir) / "piper_out.wav"
            out_path = Path(tmp_dir) / "converted.wav"
            in_path.write_bytes(wav_bytes)

            self._model.infer_file(str(in_path), str(out_path))

            return out_path.read_bytes()


voice_converter = VoiceConverter()
