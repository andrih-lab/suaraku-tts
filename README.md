# Suaraku TTS

Aplikasi web text-to-speech yang mengubah teks (Bahasa Indonesia & English)
menjadi audio dengan suara mirip suara Anda sendiri, self-hosted di VPS
Anda sendiri.

**Ini bukan speech-to-text.** Speech-to-text mengubah suara jadi tulisan.
Yang dibangun di sini kebalikannya: teks jadi suara (text-to-speech),
dengan warna suara yang dikloning dari rekaman suara Anda sendiri via RVC
(Retrieval-based Voice Conversion). Lihat `docs/ARCHITECTURE.md` untuk
detail teknisnya.

## Mulai dari mana?

1. **Baca `docs/ARCHITECTURE.md`** — pahami dulu cara kerjanya (Piper +
   RVC, kenapa dua tahap, kenapa training di Colab bukan di VPS).
2. **Rekam suara Anda** — ikuti `voice_training/RECORDING_GUIDE.md` dan
   baca kalimat-kalimat di `voice_training/sentences_id.md` +
   `sentences_en.md`. Targetkan minimal 15-20 menit rekaman bersih.
3. **Latih model suara Anda** — ikuti
   `voice_training/RVC_TRAINING_GUIDE.md` (pakai Google Colab gratis,
   20-60 menit).
4. **Deploy ke VPS Anda** — ikuti `deploy/README.md` langkah demi langkah
   (install Docker, pasang model Piper + model suara Anda, jalankan
   `docker compose up`).

## Menjalankan secara lokal (development)

Butuh Python 3.11+.

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

mkdir -p ../models/piper ../models/rvc
python3 -m piper.download_voices id_ID-news_tts-medium
python3 -m piper.download_voices en_US-lessac-medium
# (pindahkan file .onnx/.onnx.json yang terunduh ke ../models/piper/)

export MODELS_DIR=$(pwd)/../models
uvicorn app.main:app --reload
```

Buka `http://localhost:8000`. Tanpa model RVC terpasang, aplikasi tetap
jalan dan mengeluarkan suara Piper generik (belum mirip suara Anda) — ini
cara tercepat memastikan semuanya tersambung dengan benar sebelum training
suara Anda.

## Struktur proyek

```
backend/          FastAPI service: /api/tts, /api/health
frontend/         Halaman web (HTML/CSS/JS polos, tanpa framework)
voice_training/   Naskah rekaman ID+EN & panduan training RVC via Colab
deploy/           Dockerfile pendukung, docker-compose.yml, setup VPS AlmaLinux
docs/             Penjelasan arsitektur
```

## Etika & tanggung jawab

- Hanya kloning suara Anda sendiri, dengan rekaman yang Anda buat dan
  setujui sendiri.
- Jangan gunakan untuk mengkloning suara orang lain tanpa izin eksplisit
  dari mereka.
- Saat membagikan audio hasil kloning ke publik, sertakan keterangan bahwa
  audio dibuat dengan bantuan AI.
