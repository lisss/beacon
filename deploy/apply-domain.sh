#!/usr/bin/env bash
# Point the live EC2 stack at a free DuckDNS hostname.
# Usage:
#   DUCKDNS_SUBDOMAIN=jobby DUCKDNS_TOKEN=... ./deploy/apply-domain.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/deploy/.provisioned.env"
KEY_PATH="${KEY_PATH:-$HOME/.ssh/jobby-ec2}"

: "${DUCKDNS_SUBDOMAIN:?set DUCKDNS_SUBDOMAIN (e.g. jobby)}"
: "${DUCKDNS_TOKEN:?set DUCKDNS_TOKEN}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE"
  exit 1
fi
# shellcheck disable=SC1090
source "$ENV_FILE"

DOMAIN="${DUCKDNS_SUBDOMAIN}.duckdns.org"
SSH=(ssh -i "$KEY_PATH" -o StrictHostKeyChecking=accept-new "${EC2_USER}@${EC2_HOST}")

echo "==> Update DuckDNS → ${EC2_HOST}"
curl -fsS "https://www.duckdns.org/update?domains=${DUCKDNS_SUBDOMAIN}&token=${DUCKDNS_TOKEN}&ip=${EC2_HOST}"
echo

echo "==> Rewrite remote .env DOMAIN=${DOMAIN}"
"${SSH[@]}" "cat > /opt/jobby/.env" <<EOF
DOMAIN=${DOMAIN}
DUCKDNS_SUBDOMAIN=${DUCKDNS_SUBDOMAIN}
DUCKDNS_TOKEN=${DUCKDNS_TOKEN}
IMAGE=${IMAGE:-ghcr.io/lisss/jobby:latest}
REMOTIVE_ENABLED=true
EOF
"${SSH[@]}" 'chmod 600 /opt/jobby/.env'

echo "==> Restart with duckdns profile"
"${SSH[@]}" 'cd /opt/jobby && git fetch --depth 1 origin main && git reset --hard origin/main && docker compose -f docker-compose.prod.yml --profile duckdns --env-file .env up -d --force-recreate'

# persist locally
sed -i.bak "s|^DOMAIN=.*|DOMAIN=${DOMAIN}|" "$ENV_FILE" || true
grep -q '^DOMAIN=' "$ENV_FILE" || echo "DOMAIN=${DOMAIN}" >> "$ENV_FILE"
rm -f "${ENV_FILE}.bak"

echo "==> Wait for HTTPS"
for i in $(seq 1 36); do
  if curl -fsS "https://${DOMAIN}/api/health" >/dev/null 2>&1; then
    curl -fsS "https://${DOMAIN}/api/health"; echo
    echo "Live: https://${DOMAIN}"
    exit 0
  fi
  sleep 5
done
echo "Still waiting on cert — check: curl -v https://${DOMAIN}/api/health"
exit 1
