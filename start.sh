#!/usr/bin/env bash
set -euo pipefail

echo "Starting AgroVision..."

if [ ! -f .env ]; then
  echo "ERROR: .env file not found. Copy .env.example and fill in values:"
  echo "  cp .env.example .env"
  exit 1
fi

docker compose up --build "$@"
