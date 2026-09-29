# Melatih Model Suara Anda (RVC) via Google Colab

VPS Anda (4 vCPU, 4GB RAM, tanpa GPU) tidak realistis dipakai untuk
**training** model suara — bisa berjam-jam sampai berhari-hari. Training
jauh lebih cepat dengan GPU gratis dari Google Colab (biasanya 20–60 menit
untuk dataset 15–30 menit rekaman). VPS Anda hanya dipakai untuk
**inference** (generate suara sehari-hari), yang ringan dan cocok untuk CPU.

Notebook resmi dari proyek RVC:
https://colab.research.google.com/github/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/Retrieval_based_Voice_Conversion_WebUI.ipynb

Repo resminya (kalau notebook di atas pindah/berubah, cek di sini):
https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

## Langkah-langkah

1. **Siapkan rekaman**: selesaikan dulu `RECORDING_GUIDE.md`, kumpulkan
   semua file WAV rekaman Anda ke satu folder, lalu kompres jadi satu file
   `rekaman_suara_saya.zip`.

2. **Buka notebook Colab** di atas, login dengan akun Google Anda. Pastikan
   Runtime → Change runtime type → GPU (biasanya sudah default).

3. **Jalankan cell instalasi** (biasanya cell paling atas, `!git clone ...`
   dan `pip install`) — cukup jalankan berurutan dari atas, tunggu sampai
   selesai (beberapa menit).

4. **Upload rekaman Anda**: cari bagian upload dataset di notebook
   (biasanya ada widget upload file atau instruksi upload ke folder
   `dataset/`). Upload `rekaman_suara_saya.zip` dan ekstrak ke folder
   dataset sesuai instruksi notebook.

5. **Isi konfigurasi training** yang biasanya diminta notebook:
   - **Nama model**: misalnya `my_voice` (pakai nama ini konsisten, karena
     nama file model & index nanti akan memakai nama ini).
   - **Sample rate**: pilih `40k` (standar RVC v2, kualitas baik & ringan
     untuk inference di CPU nanti).
   - **Jumlah epoch**: 100–200 sudah cukup untuk dataset 15–30 menit.
     Terlalu banyak epoch dengan dataset kecil bisa membuat suara
     "overfit" (kaku, artefak aneh) — kalau itu terjadi, coba model dari
     epoch yang lebih awal.
   - **f0 method**: pilih `harvest` atau `rmvpe` (kualitas pitch tracking
     lebih baik) kalau tersedia sebagai opsi.

6. **Jalankan training** (cell "Train" / "Start Training"). Untuk dataset
   15–30 menit, biasanya selesai dalam 20–60 menit dengan GPU Colab gratis.

7. **Ambil hasilnya**: setelah selesai, notebook akan menghasilkan dua file
   penting di folder output/weights:
   - `my_voice.pth` — file model utama.
   - `my_voice.index` (atau `added_*.index`) — file index untuk kualitas
     konversi yang lebih baik. Kalau ada beberapa file `.index`, ambil yang
     ukurannya paling besar / paling baru.

   Download kedua file ini ke komputer Anda.

8. **Pasang ke VPS**: salin kedua file tersebut ke VPS Anda di
   `models/rvc/my_voice.pth` dan `models/rvc/my_voice.index` (path persis
   sesuai `backend/app/config.py`). Lihat `deploy/README.md` untuk cara
   `scp` ke VPS.

9. Restart container backend (`docker compose restart backend`) — log akan
   menunjukkan `rvc_model_loaded: true` di `/api/health` kalau berhasil
   dimuat.

## Kalau hasilnya kurang mirip

- Kualitas rekaman (noise, gema) berpengaruh lebih besar daripada jumlah
  epoch — coba rekam ulang bagian yang paling berisik.
- Tambah durasi rekaman (targetkan 30–45 menit) dan latih ulang.
- Coba beberapa checkpoint epoch berbeda (mis. epoch 100 vs 150 vs 200),
  kadang epoch lebih awal justru terdengar lebih natural.
- Sesuaikan `RVC_PITCH_SHIFT` di `.env` VPS (misalnya `-2` atau `+2`) kalau
  nada suara hasil konversi terasa terlalu tinggi/rendah dibanding suara
  asli Anda.
