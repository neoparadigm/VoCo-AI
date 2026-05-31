#!/usr/bin/env bash
# VoCo — one-command local setup
# Usage: bash setup.sh
# Requires: Python 3.11, Node 18+, and a running LLM (Ollama by default)

set -e

PYTHON=${PYTHON_BIN:-python3.11}
VENV=".venv"

echo ""
echo "VoCo setup"
echo "-------------------------------------------"

# 1. Python venv
if [ ! -d "$VENV" ]; then
  echo "-> Creating Python 3.11 venv..."
  $PYTHON -m venv $VENV
fi
source $VENV/bin/activate
echo "-> Installing backend dependencies..."
pip install -q --upgrade pip
pip install -q -r backend/requirements.txt

# 2. STT backend — auto-detect platform
ARCH=$(uname -m)
OS=$(uname -s)

if [ "$OS" = "Darwin" ] && [ "$ARCH" = "arm64" ]; then
  echo "-> Apple Silicon detected — installing mlx-whisper (Metal-accelerated)..."
  pip install -q mlx-whisper==0.4.3
elif [ -n "$VOCO_GROQ_API_KEY" ]; then
  echo "-> VOCO_GROQ_API_KEY set — installing Groq client for cloud STT..."
  pip install -q groq
elif [ -n "$VOCO_OPENAI_API_KEY" ]; then
  echo "-> VOCO_OPENAI_API_KEY set — installing OpenAI client for cloud STT..."
  pip install -q openai
else
  echo "-> CPU/GPU detected — installing faster-whisper (runs on any hardware)..."
  pip install -q faster-whisper soundfile
fi

# 3. Frontend deps
echo "-> Installing frontend dependencies..."
cd frontend && npm install --silent && cd ..

# 4. Env file
if [ ! -f ".env" ]; then
  cat > .env <<'EOF'
# ── LLM provider ──────────────────────────────────────────────────────────────
# Ollama (default) — run: ollama pull mistral
VOCO_LLM_URL=http://localhost:11434
VOCO_MODEL=mistral:latest

# OpenAI:    VOCO_LLM_URL=https://api.openai.com/v1  VOCO_MODEL=openai/gpt-4o
# Azure:     VOCO_LLM_URL=https://YOUR.openai.azure.com  VOCO_MODEL=azure/gpt-4o
# LM Studio: VOCO_LLM_URL=http://localhost:1234/v1  VOCO_MODEL=openai/local

# ── STT backend ───────────────────────────────────────────────────────────────
# auto (default) = mlx on Apple Silicon, faster-whisper elsewhere
VOCO_STT_BACKEND=auto
VOCO_WHISPER_MODEL=large-v3-turbo

# For cloud STT (uncomment one):
# VOCO_GROQ_API_KEY=gsk_...     # Groq — free tier, ~300ms
# VOCO_OPENAI_API_KEY=sk-...    # OpenAI Whisper API
EOF
  echo "-> Created .env — edit to configure your LLM and STT backend"
fi

echo ""
echo "Setup complete."
echo ""
echo "Run VoCo:"
echo "  Terminal 1: source .venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Open: http://localhost:3000"
echo ""
