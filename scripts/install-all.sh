#!/usr/bin/env bash
set -euo pipefail
DEV=0
EXCEL=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev) DEV=1; shift ;;
    --excel) EXCEL=1; shift ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

python -m pip install --upgrade pip
python -m pip install -r requirements-core.txt

if [[ $EXCEL -eq 1 ]]; then
  python -m pip install -r requirements-excel.txt
fi
if [[ $DEV -eq 1 ]]; then
  python -m pip install -r requirements-dev.txt
fi

echo "Installation complete."
