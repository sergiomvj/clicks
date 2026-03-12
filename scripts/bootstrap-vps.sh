#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/fbr-click}"
DOMAIN_FRONT="${DOMAIN_FRONT:-click.fbrapps.com}"
DOMAIN_API="${DOMAIN_API:-api.click.fbrapps.com}"
EMAIL="${CERTBOT_EMAIL:-admin@fbrapps.com}"

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release nginx certbot python3-certbot-nginx

install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
fi

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker

mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/docker/certs"
mkdir -p /var/log/fbr-click

if ! command -v certbot >/dev/null 2>&1; then
  apt-get install -y certbot python3-certbot-nginx
fi

certbot certonly --nginx --non-interactive --agree-tos --email "$EMAIL" -d "$DOMAIN_FRONT" -d "$DOMAIN_API"

cat <<EOF
Bootstrap concluido.

Proximos passos:
1. copiar o projeto para $APP_DIR
2. copiar .env.production.example para .env e preencher secrets reais
3. subir com: docker compose -f docker-compose.production.yml up -d --build
4. rodar smoke test: powershell -ExecutionPolicy Bypass -File .\\scripts\\smoke-deploy.ps1
EOF
