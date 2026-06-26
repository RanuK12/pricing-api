#!/usr/bin/env bash
# setup-droplet.sh — Crear droplet en DO y deployar Pricing API
# Requiere: doctl configurado con token de DigitalOcean
# Uso: ./setup-droplet.sh

set -euo pipefail

DROPLET_NAME="pricing-api"
REGION="nyc1"
SIZE="s-1vcpu-1gb"
IMAGE="docker-20-04"

echo "→ Creando droplet '$DROPLET_NAME'..."
DROPLET=$(doctl compute droplet create "$DROPLET_NAME" \
  --region "$REGION" \
  --size "$SIZE" \
  --image "$IMAGE" \
  --ssh-keys "$(doctl compute ssh-key list --no-header --format ID | head -1)" \
  --wait \
  --format "ID,PublicIPv4,Status" \
  --no-header 2>&1)

IP=$(echo "$DROPLET" | awk '{print $2}')
echo "→ Droplet creado: $IP"

echo "→ Esperando SSH..."
for i in $(seq 1 10); do
  if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "root@$IP" "echo ready" 2>/dev/null; then
    break
  fi
  sleep 5
done

echo "→ Deployando API..."
cd "$(dirname "$0")"
./deploy.sh "$IP"

echo ""
echo "✅ Pricing API lista en: http://$IP:8000"
echo "   Docs: http://$IP:8000/docs"
