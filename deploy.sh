#!/usr/bin/env bash

set -e

echo "====================================="
echo " FASTAPI DOCENCIA DEPLOY"
echo "====================================="

PROJECT_DIR="/home/matrix/Programas/fastapi-docencia"
VENV_DIR="$PROJECT_DIR/.venv"

cd "$PROJECT_DIR"

echo ""
echo "[1/6] Actualizando repositorio..."
git pull origin main

echo ""
echo "[2/6] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo ""
echo "[3/6] Actualizando pip..."
pip install --upgrade pip

echo ""
echo "[4/6] Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "[5/6] Recargando systemd..."
sudo systemctl daemon-reload

echo ""
echo "[6/6] Reiniciando servicio..."
sudo systemctl restart fastapi-docencia

echo ""
echo "====================================="
echo " DEPLOY COMPLETADO CORRECTAMENTE"
echo "====================================="