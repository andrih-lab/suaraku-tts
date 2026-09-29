#!/usr/bin/env bash
# Tempel & jalankan skrip ini sebagai root di VPS AlmaLinux 10 Anda
# (via VNC Console panel VPS Anda). Skrip ini akan:
#   1. Install Docker
#   2. Siapkan swap 4GB (karena RAM VPS cuma 4GB)
#   3. Clone/update aplikasi Suaraku TTS
#   4. Unduh suara dasar Piper (Indonesia + Inggris)
#   5. Bersihkan sisa build Docker dari percobaan sebelumnya (hemat disk)
#   6. Jalankan aplikasi lewat Docker
#   7. Pasang Nginx + sertifikat HTTPS (Let's Encrypt) untuk domain di bawah
#
# Aman dijalankan berulang kali (idempotent) -- kalau ada langkah yang
# gagal, perbaiki masalahnya lalu jalankan skrip ini lagi dari awal.

set -euo pipefail

DOMAIN="suara.andrihendrizal.com"
CERTBOT_EMAIL="andri.hendrizal@gmail.com"
REPO_URL="https://github.com/andrih-lab/suaraku-tts.git"
APP_DIR="/root/suaraku-tts"

echo "=============================================="
echo "[1/6] Install Docker"
echo "=============================================="
dnf -y install dnf-plugins-core git curl
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

echo "=============================================="
echo "[2/6] Siapkan swap 4GB"
echo "=============================================="
if [ ! -f /swapfile ]; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
else
  echo "Swap sudah ada, lewati."
fi

echo "=============================================="
echo "[3/6] Ambil aplikasi Suaraku TTS"
echo "=============================================="
if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR" && git pull
else
  rm -rf "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

echo "=============================================="
echo "[4/6] Unduh suara dasar Piper (ID + EN)"
echo "=============================================="
mkdir -p "$APP_DIR/models/piper" "$APP_DIR/models/rvc"
if [ ! -f "$APP_DIR/models/piper/id_ID-news_tts-medium.onnx" ]; then
  python3 -m venv /tmp/piper-dl-venv
  /tmp/piper-dl-venv/bin/pip install --quiet --upgrade pip piper-tts
  cd "$APP_DIR/models/piper"
  /tmp/piper-dl-venv/bin/python3 -m piper.download_voices id_ID-news_tts-medium
  /tmp/piper-dl-venv/bin/python3 -m piper.download_voices en_US-lessac-medium
  cd "$APP_DIR"
else
  echo "Suara Piper sudah terunduh, lewati."
fi

echo "=============================================="
echo "[5/7] Bersihkan sisa build Docker sebelumnya"
echo "=============================================="
echo "Ruang disk sebelum dibersihkan:"
df -h / | tail -1
docker system prune -af 2>/dev/null || true
echo "Ruang disk setelah dibersihkan:"
df -h / | tail -1

echo "=============================================="
echo "[6/7] Jalankan aplikasi (Docker)"
echo "=============================================="
cd "$APP_DIR/deploy"
docker compose up -d --build

echo "=============================================="
echo "[7/7] Pasang Nginx + HTTPS untuk $DOMAIN"
echo "=============================================="
dnf -y install nginx certbot python3-certbot-nginx

cat > /etc/nginx/conf.d/suaraku.conf <<NGINX
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX

systemctl enable --now nginx
firewall-cmd --permanent --add-service=http --add-service=https 2>/dev/null || true
firewall-cmd --reload 2>/dev/null || true

SERVER_IP=$(curl -s https://api.ipify.org || echo "unknown")
RESOLVED_IP=$(getent hosts "$DOMAIN" 2>/dev/null | awk '{print $1}' || true)

echo ""
echo "=============================================="
if [ "$RESOLVED_IP" = "$SERVER_IP" ]; then
  echo "DNS $DOMAIN sudah mengarah ke server ini. Memasang sertifikat SSL..."
  certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$CERTBOT_EMAIL" --redirect
  echo ""
  echo "SELESAI! Buka: https://$DOMAIN"
else
  echo "Aplikasi sudah jalan, TAPI DNS $DOMAIN belum mengarah ke server ini."
  echo "  IP server ini   : $SERVER_IP"
  echo "  DNS saat ini    : ${RESOLVED_IP:-belum ada / tidak ditemukan}"
  echo ""
  echo "Untuk sementara bisa diakses lewat: http://$SERVER_IP:8000"
  echo ""
  echo "Perbaiki dulu DNS suara.andrihendrizal.com (lihat panduan Netlify DNS),"
  echo "tunggu 5-30 menit sampai menyebar, lalu jalankan perintah ini untuk"
  echo "memasang SSL:"
  echo ""
  echo "  certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $CERTBOT_EMAIL --redirect"
fi
echo "=============================================="

echo ""
echo "Cek status kesehatan aplikasi:"
curl -s http://localhost:8000/api/health || echo "(gagal, cek: docker compose logs -f di $APP_DIR/deploy)"
