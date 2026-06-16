#!/usr/bin/env bash
set -euo pipefail

echo "Restarting AgroVision..."
docker compose down
docker compose up --build "$@"
