#!/bin/bash
# MuseGen GPU Services
DATA_DIR="/root/autodl-tmp"
LOG_DIR="$DATA_DIR/logs"
mkdir -p $LOG_DIR

echo "===== MuseGen GPU Server Starting ====="

echo "[1/3] Starting Ollama..."
export OLLAMA_MODELS="$DATA_DIR/ollama_models"
nohup ollama serve > $LOG_DIR/ollama.log 2>&1 &
sleep 2
pgrep -f "ollama serve" > /dev/null && echo "  Ollama: OK (11434)" || echo "  Ollama: FAILED"

echo "[2/3] Starting ComfyUI..."
cd $DATA_DIR/ComfyUI
nohup /root/miniconda3/bin/python3 main.py --listen 0.0.0.0 --port 8188 > $LOG_DIR/comfyui.log 2>&1 &
sleep 3
pgrep -f "main.py" > /dev/null && echo "  ComfyUI: OK (8188)" || echo "  ComfyUI: FAILED"

echo "[3/3] Starting CosyVoice..."
cd $DATA_DIR/CosyVoice
COSYVOICE_PORT=5000 nohup /root/miniconda3/bin/python3 server.py > $LOG_DIR/cosyvoice.log 2>&1 &
sleep 2
pgrep -f "server.py" > /dev/null && echo "  CosyVoice: OK (5000)" || echo "  CosyVoice: FAILED"

echo "===== All services started ====="
echo "Ollama: http://127.0.0.1:11434"
echo "ComfyUI: http://127.0.0.1:8188"
echo "CosyVoice: http://127.0.0.1:5000"
