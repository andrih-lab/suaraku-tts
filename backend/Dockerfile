FROM python:3.11-slim

# libsndfile1: needed by `soundfile`. ffmpeg: needed by rvc-python for some
# audio format handling.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build context is the project root (see deploy/docker-compose.yml) so this
# Dockerfile can reach both backend/ and frontend/.
COPY backend/requirements.txt .

# Install the CPU-only PyTorch wheel explicitly. Without this, pip may pull
# the much larger CUDA build, wasting disk and RAM on a GPU-less VPS.
RUN pip install --no-cache-dir torch==2.4.1 torchaudio==2.4.1 \
      --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY frontend /app/frontend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
