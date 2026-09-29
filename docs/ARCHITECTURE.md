# Arsitektur

```
Teks (ID/EN)
     |
     v
[Piper TTS]  -- suara generik, tapi intonasi & pelafalan sudah natural
     |
     v
[RVC voice conversion]  -- warna suara diubah jadi suara Anda,
     |                      berdasarkan model hasil training dari rekaman Anda
     v
Audio WAV (suara Anda, ID/EN)
```

## Kenapa dua tahap, bukan satu model kloning langsung?

Model kloning suara "satu langkah" yang berkualitas tinggi (mis. XTTS-v2)
umumnya butuh beberapa GB RAM dan idealnya GPU untuk kecepatan yang wajar.
VPS di proyek ini sengaja disiapkan tanpa GPU dan hanya 4GB RAM, sehingga:

- **Piper** menangani bagian "bicara dengan benar" (linguistik, intonasi,
  pelafalan ID & EN) — modelnya kecil (~50-100MB) dan sangat cepat di CPU.
- **RVC** menangani bagian "terdengar seperti saya" (warna suara/timbre) —
  modelnya juga relatif kecil dan inference-nya cukup cepat di CPU
  (training-nya yang berat, makanya dilakukan sekali di Google Colab, lihat
  `voice_training/RVC_TRAINING_GUIDE.md`).

Hasilnya: kebutuhan resource untuk pemakaian sehari-hari (inference) tetap
ringan dan realistis untuk VPS 4GB RAM tanpa GPU.

## Struktur folder

```
backend/         FastAPI service (app/main.py, tts_piper.py, voice_convert.py)
frontend/        Halaman web statis (di-serve oleh backend yang sama)
voice_training/  Naskah rekaman + panduan training RVC di Colab
deploy/          Dockerfile pendukung, docker-compose.yml, setup VPS
models/          (tidak di-commit) taruh file model Piper & RVC di sini
```

## Kalau ingin upgrade kualitas nanti

- Tambah GPU ke VPS (atau pindah ke VPS ber-GPU) → bisa ganti Piper+RVC
  dengan model kloning zero-shot satu-tahap (mis. XTTS-v2 / OpenVoice V2)
  untuk kualitas lebih tinggi tanpa perlu training terpisah per suara.
- Latih ulang model RVC dengan lebih banyak rekaman (30-60 menit) untuk
  hasil yang lebih stabil dan mirip.
