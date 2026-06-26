#!/usr/bin/env bash
# deploy.sh — Deploy reproducible de Pricing API a DigitalOcean
# Uso: ./deploy.sh <ip_del_droplet>
# Ej:  ./deploy.sh 157.230.190.189

set -euo pipefail

IP="${1:-}"
if [ -z "$IP" ]; then
  echo "Uso: $0 <ip_del_droplet>"
  exit 1
fi

echo "→ Comprimiendo código..."
tar czf /tmp/pricing-api-deploy.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='.venv' \
  -C "$(dirname "$0")" .

echo "→ Subiendo a $IP..."
ssh "root@$IP" "mkdir -p /opt/pricing-api"
scp /tmp/pricing-api-deploy.tar.gz "root@$IP:/opt/pricing-api/"

echo "→ Extrayendo y levantando..."
ssh "root@$IP" bash -c "'
  cd /opt/pricing-api
  rm -f ._*
  tar xzf pricing-api-deploy.tar.gz
  rm pricing-api-deploy.tar.gz
  docker compose up -d --build
'"

echo "→ Esperando healthcheck..."
sleep 5
curl -sf "http://$IP:8000/health" && echo "✅ Deploy exitoso!" || echo "⚠️  Healthcheck no responde aún"
