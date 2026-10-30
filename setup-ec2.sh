#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo " AnyDown — Automated EC2 Setup & Deployment"
echo "=========================================================="

# 1. Update OS and install essential tools
echo "[1/6] Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg git lsb-release

# 2. Add 2GB swap space (prevents OOM during Next.js builds on micro/small instances)
if [ ! -f /swapfile ]; then
  echo "[2/6] Configuring 2GB swap file to prevent out-of-memory errors during builds..."
  sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
else
  echo "[2/6] Swapfile already exists."
fi

# 3. Install Docker and Docker Compose Plugin
if ! command -v docker &> /dev/null; then
  echo "[3/6] Installing Docker..."
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo systemctl enable docker
  sudo systemctl start docker
  sudo usermod -aG docker "${USER:-ubuntu}"
else
  echo "[3/6] Docker is already installed."
fi

# 4. Determine Project Directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 5. Build and launch containers
echo "[4/6] Building and starting AnyDown containers (backend, frontend, nginx)..."
if docker compose version &> /dev/null; then
  sudo docker compose down --remove-orphans || true
  sudo docker compose up -d --build
elif command -v docker-compose &> /dev/null; then
  sudo docker-compose down --remove-orphans || true
  sudo docker-compose up -d --build
else
  echo "Error: Docker compose command not found!"
  exit 1
fi

# 6. Verify health
echo "[5/6] Waiting for services to become healthy..."
MAX_ATTEMPTS=24
COUNT=0
HEALTHY=false

while [ $COUNT -lt $MAX_ATTEMPTS ]; do
  if curl -sSf http://127.0.0.1/api/v1/health > /dev/null 2>&1; then
    HEALTHY=true
    break
  fi
  COUNT=$((COUNT + 1))
  sleep 5
done

PUBLIC_IP=$(curl -s https://checkip.amazonaws.com || curl -s ifconfig.me || echo "localhost")

echo "=========================================================="
if [ "$HEALTHY" = true ]; then
  echo " SUCCESS! AnyDown is live on AWS EC2!"
  echo " Website URL: http://${PUBLIC_IP}"
  echo " API Health:  http://${PUBLIC_IP}/api/v1/health"
else
  echo " Containers started. Health check is still warming up."
  echo " Check container status with: sudo docker compose ps"
  echo " Website URL: http://${PUBLIC_IP}"
fi
echo "=========================================================="

