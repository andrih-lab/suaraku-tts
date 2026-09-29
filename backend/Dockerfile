FROM python:3.12-slim

# git: needed to clone Applio. libsndfile1: needed by `soundfile`.
# ffmpeg: needed for audio format handling.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Voice conversion engine (Applio, a maintained RVC fork) ---
# Pinned to a release tag (not `main`) so this build doesn't silently break
# when upstream changes. Applio provides the `core.py infer` CLI our backend
# shells out to (see app/voice_convert.py) -- CLI args are a much more
# stable integration point than importing its internal Python modules.
RUN git clone --depth 1 --branch 3.6.5 https://github.com/IAHispano/Applio.git /app/applio

# Install the CPU-only PyTorch wheel explicitly, matching the exact version
# Applio's requirements.txt pins. Without --index-url ...cpu, pip pulls the
# much larger CUDA build (2.5+ GB of unused nvidia-* packages on a GPU-less
# VPS) because torchaudio's normal PyPI wheel depends on default torch.
RUN pip install --no-cache-dir torch==2.11.0 torchaudio==2.11.0 \
      --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r /app/applio/requirements.txt

# Downloads Applio's pretrained HuBERT/RMVPE/HiFi-GAN weights at build time
# (baked into the image) so the first real request doesn't stall on a
# multi-hundred-MB download.
RUN cd /app/applio && python3 core.py prerequisites

# --- Our own lightweight backend (FastAPI + Piper) ---
COPY backend/requirements.txt ./backend-requirements.txt
RUN pip install --no-cache-dir -r backend-requirements.txt

COPY backend/app ./app
COPY frontend /app/frontend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
