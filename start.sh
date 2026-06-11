#!/bin/bash
# start.sh — Inicia o Bolão Copa 2026

export SECRET_KEY="${SECRET_KEY:-bolao-copa-2026-mude-isso}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin2026}"
export PORT="${PORT:-5000}"

cd "$(dirname "$0")/backend"
echo ""
echo "⚽ ======================================"
echo "   Bolão Copa 2026 — Iniciando..."
echo "======================================="
echo "   Participantes: http://localhost:$PORT"
echo "   Admin:         http://localhost:$PORT/admin"
echo "   Senha admin:   $ADMIN_PASSWORD"
echo "======================================="
echo ""
python3 app.py
