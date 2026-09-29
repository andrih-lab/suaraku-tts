# Panduan Rekaman Suara

Rekaman ini akan menjadi bahan untuk melatih model kloning suara Anda (RVC).
Kualitas rekaman jauh lebih penting daripada jumlahnya — 20 menit rekaman
bersih jauh lebih baik daripada 1 jam rekaman berisik.

## Alat & Setting

- **Mikrofon**: headset/earphone dengan mic bawaan sudah cukup untuk mulai;
  mic USB kondenser (mis. Fifine, Blue Yeti) akan memberi hasil lebih baik.
  Hindari mic internal laptop kalau bisa.
- **Ruangan**: ruangan kecil dengan banyak benda lunak (kasur, lemari
  pakaian, karpet, tirai) — ini meredam gema. Hindari ruangan kosong/keramik
  yang bergema, dan hindari kipas angin/AC yang berisik saat rekam.
- **Jarak mic**: konsisten, sekitar 10–15 cm dari mulut, sedikit menyamping
  agar tidak ada suara "plosif" (letupan p/b) yang pecah.
- **Format**: rekam sebagai **WAV, mono, 44.1kHz atau 48kHz, 16-bit**.
  Aplikasi perekam yang gampang: Voice Recorder bawaan HP (lalu convert ke
  WAV), Audacity (gratis, PC/Mac/Linux), atau aplikasi "Recorder" di HP.
- **Cara bicara**: bicara dengan **nada & gaya bicara natural Anda
  sehari-hari** — jangan dibuat-buat, jangan terlalu formal atau terlalu
  pelan. Model akan meniru persis apa yang Anda rekam, termasuk intonasi.
- Beri jeda ~1 detik hening di awal dan akhir setiap kalimat. Kalau salah
  ucap, berhenti, tarik napas, ulangi kalimat dari awal (jangan disambung).
- Satu file per kalimat lebih mudah diproses, tapi merekam mengalir lalu
  dipotong-potong nanti juga boleh — yang penting tiap kalimat jelas
  batasnya.

## Target

- Minimal **~15–20 menit** total (gabungan ID + EN) untuk hasil awal yang
  layak.
- **30+ menit** untuk hasil yang lebih mirip & lebih stabil.
- Baca kalimat pada kedua daftar di bawah (`sentences_id.md` dan
  `sentences_en.md`). Tidak perlu semua kalimat kalau waktu terbatas —
  prioritaskan variasi (pernyataan, pertanyaan, seruan, kalimat pendek &
  panjang) daripada jumlah.

## Setelah selesai rekam

1. Kumpulkan semua file WAV ke dalam satu folder, misalnya
   `rekaman_suara_saya/`.
2. Dengarkan ulang sekilas, buang file yang ada suara batuk/berisik/salah
   ucap parah.
3. Lanjut ke `RVC_TRAINING_GUIDE.md` untuk melatih model dari rekaman ini.

## Etika & Persetujuan

Model suara ini meniru suara Anda sendiri berdasarkan rekaman yang Anda
buat dan setujui sendiri. Jangan gunakan proses yang sama untuk mengkloning
suara orang lain tanpa izin eksplisit dari mereka — di banyak yurisdiksi
ini bisa melanggar hukum (penyalahgunaan identitas/hak suara) selain tidak
etis. Saat membagikan audio hasil kloning ke publik, sebaiknya sertakan
keterangan bahwa audio dibuat dengan bantuan AI.
