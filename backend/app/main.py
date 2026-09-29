import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from . import config
from .schemas import HealthResponse, TTSRequest
from .tts_piper import piper_engine
from .voice_convert import voice_converter


@asynccontextmanager
async def lifespan(app: FastAPI):
    piper_engine.load()
    voice_converter.load()
    yield


app = FastAPI(title="Suaraku TTS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        piper_voices_loaded=piper_engine.loaded_languages(),
        rvc_model_loaded=voice_converter.is_ready(),
    )


@app.post("/api/tts")
def synthesize(req: TTSRequest) -> Response:
    if len(req.text) > config.MAX_TEXT_LENGTH:
        raise HTTPException(400, f"Text too long (max {config.MAX_TEXT_LENGTH} characters).")

    if req.language not in piper_engine.loaded_languages():
        raise HTTPException(
            503,
            f"Voice for language '{req.language}' isn't installed on the server yet.",
        )

    try:
        audio = piper_engine.synthesize_to_wav_bytes(req.text, req.language)
        if req.clone_voice:
            audio = voice_converter.convert(audio)
    except Exception as exc:  # noqa: BLE001 -- surfaced to the caller deliberately
        raise HTTPException(500, f"Speech generation failed: {exc}") from exc

    return Response(content=audio, media_type="audio/wav")


@app.post("/api/upload-voice-model")
async def upload_voice_model(
    token: str = Form(...),
    pth_file: UploadFile = File(...),
    index_file: UploadFile = File(...),
) -> dict:
    if not config.UPLOAD_TOKEN or not secrets.compare_digest(token, config.UPLOAD_TOKEN):
        raise HTTPException(403, "Invalid upload token.")

    if not pth_file.filename.endswith(".pth"):
        raise HTTPException(400, "First file must be a .pth file.")
    if not index_file.filename.endswith(".index"):
        raise HTTPException(400, "Second file must be a .index file.")

    for upload in (pth_file, index_file):
        upload.file.seek(0, os.SEEK_END)
        if upload.file.tell() > config.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(400, f"{upload.filename} is too large.")
        upload.file.seek(0)

    config.RVC_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.RVC_MODEL_PATH.write_bytes(await pth_file.read())
    config.RVC_INDEX_PATH.write_bytes(await index_file.read())

    # No restart needed: voice_converter checks these paths fresh on every
    # /api/tts request.
    return {"status": "ok", "rvc_model_loaded": voice_converter.is_ready()}


# Serve the static frontend (index.html, app.js, style.css) at "/".
# /app/frontend is where the Dockerfile copies it; the repo-root fallback
# lets `uvicorn app.main:app` work for local dev without extra setup.
_docker_frontend = Path("/app/frontend")
_dev_frontend = Path(__file__).resolve().parent.parent.parent / "frontend"
_frontend_dir = Path(os.environ.get("FRONTEND_DIR", _docker_frontend if _docker_frontend.exists() else _dev_frontend))
app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
