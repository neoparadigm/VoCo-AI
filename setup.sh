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

# 2. Frontend deps
echo "-> Installing frontend dependencies..."
cd frontend && npm install --silent && cd ..

# 3. Env file
if [ ! -f ".env" ]; then
  cat > .env <<'EOF'
# LLM provider — Ollama (default) or any OpenAI-compatible endpoint
VOCO_LLM_URL=http://localhost:11434
VOCO_MODEL=mistral:latest

# OpenAI:    VOCO_LLM_URL=https://api.openai.com/v1  VOCO_MODEL=openai/gpt-4o
# Anthropic: VOCO_LLM_URL=https://...                VOCO_MODEL=anthropic/claude-opus-4-6
EOF
  echo "-> Created .env — edit to configure your LLM"
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
