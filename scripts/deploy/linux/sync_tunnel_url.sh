#!/usr/bin/env bash
set -euo pipefail

REPO="apmauj/sifu"

info(){ echo "[INFO] $*"; }
ok(){ echo "[OK]   $*"; }
err(){ echo "[ERR]  $*"; }

for cmd in docker gh curl; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "Falta comando: $cmd"
    exit 1
  fi
done

if ! gh auth status >/dev/null 2>&1; then
  err "gh no autenticado"
  exit 1
fi

logs="$(docker logs --tail 220 sifu-tunnel 2>&1 || true)"
url="$(printf '%s' "$logs" | grep -Eo 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' | tail -n1 || true)"

if [[ -z "$url" ]]; then
  err "No se detectó URL trycloudflare en logs"
  exit 1
fi

health_url="$url/api/health/simple"
ok_health=false
for delay in 8 15 30 45 60 90; do
  info "Health check: $health_url"
  if curl -fsS --max-time 12 "$health_url" >/dev/null 2>&1; then
    ok_health=true
    break
  fi
  info "Aún no disponible, reintento en ${delay}s"
  sleep "$delay"
done

if [[ "$ok_health" != true ]]; then
  err "No pasó health check tras reintentos"
  exit 1
fi

printf '%s' "$url" | gh secret set VITE_PUBLIC_API_URL -R "$REPO" >/dev/null
ok "Secret VITE_PUBLIC_API_URL actualizado: $url"

gh workflow run .github/workflows/ci-cd.yml -R "$REPO" -f force_frontend_deploy=true >/dev/null
ok "CI/CD disparado (force_frontend_deploy=true)"
