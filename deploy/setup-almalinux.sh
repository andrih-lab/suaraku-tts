#!/usr/bin/env bash
# Run this once on a fresh AlmaLinux 10 VPS to install Docker + Compose,
# and set up swap (recommended: your VPS only has 4GB RAM, and loading
# PyTorch + models can spike memory usage).
set -euo pipefail

echo "== Installing Docker Engine =="
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker

echo "== Adding current user to the docker group (log out/in to apply) =="
sudo usermod -aG docker "$USER"

echo "== Setting up 4GB swap (recommended on a 4GB-RAM VPS) =="
if [ ! -f /swapfile ]; then
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
else
  echo "/swapfile already exists, skipping."
fi

echo "== Opening firewall port 8000 (adjust if you put Nginx in front) =="
sudo firewall-cmd --permanent --add-port=8000/tcp || true
sudo firewall-cmd --reload || true

echo "Done. Log out and back in for the docker group change to take effect,"
echo "then continue with deploy/README.md."
