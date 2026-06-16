#!/usr/bin/env bash
set -euo pipefail

echo "Stopping AgroVision..."
docker compose down "$@"
echo "Done."
