from typing import Literal

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    language: Literal["id", "en"] = "id"
    clone_voice: bool = True


class HealthResponse(BaseModel):
    status: str
    piper_voices_loaded: list[str]
    rvc_model_loaded: bool
