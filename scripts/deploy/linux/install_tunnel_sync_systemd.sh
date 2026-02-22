#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="sifu-tunnel-sync.service"
TIMER_NAME="sifu-tunnel-sync.timer"

if [[ $EUID -ne 0 ]]; then
  echo "[ERR] Ejecuta este script como root (sudo)."
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Uso: sudo ./scripts/deploy/linux/install_tunnel_sync_systemd.sh /ruta/al/repo"
  exit 1
fi

REPO_PATH="$1"
UNIT_DIR="/etc/systemd/system"
SCRIPT_PATH="$REPO_PATH/scripts/deploy/linux/sync_tunnel_url.sh"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "[ERR] No existe script: $SCRIPT_PATH"
  exit 1
fi

cat > "$UNIT_DIR/$SERVICE_NAME" <<EOF
[Unit]
Description=SIFU tunnel URL sync to GitHub
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$REPO_PATH
ExecStart=/usr/bin/env bash $SCRIPT_PATH
EOF

cat > "$UNIT_DIR/$TIMER_NAME" <<EOF
[Unit]
Description=Run SIFU tunnel sync at boot and periodically

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
Persistent=true
Unit=$SERVICE_NAME

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now "$TIMER_NAME"

echo "[OK] Instalado $SERVICE_NAME y $TIMER_NAME"
systemctl status "$TIMER_NAME" --no-pager || true
