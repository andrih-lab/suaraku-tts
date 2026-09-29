# Deploy ke VPS AlmaLinux 10

Panduan ini untuk VPS spek: 4 vCPU, 4GB RAM, 30GB storage, AlmaLinux 10,
tanpa GPU.

## Cara termudah: satu skrip, tanpa perlu paham Linux

Kalau Anda tidak familiar dengan Linux/SSH, pakai jalur ini:

1. Login ke panel VPS Anda (mis. `manage.plasawebhost.com/clientarea.php`),
   buka detail VPS Anda, lalu buka **VNC Console** (terminal langsung di
   browser, tidak perlu install apa pun). Kalau tidak tahu/lupa password
   root, pakai dulu tombol **Ganti Password VPS** di panel yang sama.
2. Login di jendela VNC sebagai `root` dengan password tersebut.
3. Di terminal VNC itu, ketik/paste satu baris ini lalu Enter:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/andrih-lab/suaraku-tts/main/deploy/one-shot-install.sh | bash
   ```
4. Tunggu sampai selesai (build Docker pertama kali bisa 20-30 menit --
   mesin voice conversion-nya cukup besar).
   Skrip ini otomatis: install Docker, siapkan swap, ambil aplikasi,
   unduh suara dasar (ID+EN), jalankan aplikasi, dan pasang Nginx + HTTPS
   untuk `suara.andrihendrizal.com` (kalau DNS-nya sudah mengarah ke VPS
   ini -- lihat bagian DNS di bawah).
5. Kalau di akhir skrip muncul pesan DNS belum mengarah ke server ini,
   perbaiki dulu DNS-nya (lihat di bawah), tunggu 5-30 menit, lalu jalankan
   ulang baris `certbot ...` yang ditampilkan skrip.
6. Skrip juga mencetak **kode upload** (sekali, acak) di akhir prosesnya --
   simpan/screenshot itu. Nanti dipakai di `https://suara.andrihendrizal.com/upload.html`
   untuk mengaktifkan suara Anda sendiri (lihat `voice_training/RVC_TRAINING_GUIDE.md`
   langkah terakhir) -- tanpa perlu masuk ke VPS lagi.

### Arahkan suara.andrihendrizal.com ke VPS ini (DNS di Netlify)

1. Buka dashboard Netlify → **Domains** (atau **Team → DNS**) → pilih
   `andrihendrizal.com` → tab **DNS records**.
2. Cari record untuk `suara` (subdomain yang sudah Anda buat). Hapus kalau
   isinya mengarah ke Netlify (mis. CNAME ke `*.netlify.app`).
3. Tambah record baru:
   - **Type**: `A`
   - **Name**: `suara`
   - **Value**: `103.151.140.152` (IP VPS Anda)
   - **TTL**: biarkan default
4. Simpan. Propagasi biasanya 5-30 menit (kadang sampai beberapa jam).
   Cek dengan `nslookup suara.andrihendrizal.com` dari komputer mana pun.

Setelah langkah-langkah di atas, cukup buka `https://suara.andrihendrizal.com`.

---

## Cara manual (kalau familiar dengan SSH/terminal)

### 1. Setup awal server (sekali saja)

SSH ke VPS Anda, lalu:

```bash
git clone https://github.com/andrih-lab/suaraku-tts.git
cd suaraku-tts
chmod +x deploy/setup-almalinux.sh
./deploy/setup-almalinux.sh
```

Log out lalu SSH masuk lagi (supaya keanggotaan grup `docker` aktif).

### 2. Siapkan model suara

Di server, buat folder model:

```bash
mkdir -p ~/suaraku-tts/models/piper ~/suaraku-tts/models/rvc
```

**Piper (base TTS, dua bahasa):**

```bash
cd ~/suaraku-tts/models/piper
pip install --user piper-tts   # kalau python3/pip belum ada: sudo dnf install -y python3-pip
python3 -m piper.download_voices id_ID-news_tts-medium
python3 -m piper.download_voices en_US-lessac-medium
```

Ini akan mengunduh 4 file `.onnx` + `.onnx.json` ke folder ini.

**RVC (suara Anda):** ikuti `voice_training/RECORDING_GUIDE.md` dan
`voice_training/RVC_TRAINING_GUIDE.md` terlebih dahulu (training dilakukan
di Google Colab, bukan di VPS). Setelah selesai, cara termudah adalah
upload kedua file lewat `https://suara.andrihendrizal.com/upload.html`
(butuh kode upload -- lihat `echo "UPLOAD_TOKEN=..." > deploy/.env` di
bawah kalau Anda deploy manual). Alternatif via terminal:

```bash
scp my_voice.pth my_voice.index user@VPS_IP:~/suaraku-tts/models/rvc/
```

Tanpa file ini, aplikasi tetap jalan tapi hanya mengeluarkan suara Piper
generik (belum mirip suara Anda) — berguna untuk tes awal bahwa server
sudah jalan dengan benar.

**Kode upload** (untuk halaman `/upload.html`) diambil dari `UPLOAD_TOKEN`
di `deploy/.env`. Kalau Anda deploy manual (bukan lewat `one-shot-install.sh`,
yang membuatnya otomatis), buat sendiri:

```bash
echo "UPLOAD_TOKEN=$(openssl rand -hex 16)" > ~/suaraku-tts/deploy/.env
```

### 3. Jalankan aplikasi

```bash
cd ~/suaraku-tts/deploy
docker compose up -d --build
```

Build pertama kali akan memakan waktu (mengunduh image Python + PyTorch
CPU + Applio + dependensinya) — bisa 20-30 menit tergantung koneksi VPS.

Cek statusnya:

```bash
curl http://localhost:8000/api/health
```

Harus muncul `"piper_voices_loaded": ["id", "en"]` dan (setelah model RVC
terpasang) `"rvc_model_loaded": true`.

Buka `http://IP_VPS_ANDA:8000` di browser untuk memakai aplikasinya.

### 4. (Opsional tapi disarankan) Nginx + domain + HTTPS

Mengekspos port 8000 langsung ke internet tanpa HTTPS berarti teks dan
audio Anda dikirim tanpa enkripsi. Kalau Anda punya domain, pasang Nginx
sebagai reverse proxy + Let's Encrypt:

```bash
sudo dnf -y install nginx
sudo dnf -y install certbot python3-certbot-nginx
```

Buat file `/etc/nginx/conf.d/suaraku.conf`:

```nginx
server {
    listen 80;
    server_name suara.domainanda.com;

    # Model suara (.pth) bisa puluhan-ratusan MB -- default Nginx (1MB)
    # akan menolak upload tanpa ini.
    client_max_body_size 600M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Lalu:

```bash
sudo systemctl enable --now nginx
sudo certbot --nginx -d suara.domainanda.com
sudo firewall-cmd --permanent --add-service=http --add-service=https
sudo firewall-cmd --reload
```

Setelah ini, tutup akses langsung ke port 8000 dari luar (hanya izinkan
dari localhost), karena publik seharusnya lewat Nginx di port 80/443.

## Perawatan

- **Update kode**: `git pull && docker compose up -d --build`
- **Lihat log**: `docker compose logs -f backend`
- **Ganti model suara**: upload lewat `/upload.html`, atau timpa langsung
  file di `models/rvc/` -- tidak perlu restart, terbaca otomatis di
  permintaan berikutnya.
- **Cek pemakaian RAM**: `docker stats` — kalau sering penuh, VPS akan
  memakai swap (lebih lambat tapi tidak crash); pertimbangkan upgrade RAM
  kalau ini sering terjadi.
