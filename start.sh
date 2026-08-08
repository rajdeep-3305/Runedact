#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "Starting Runedact..."

# Find the virtual environment (repo root or backend/)
if [ -d "$ROOT_DIR/.venv" ]; then
    VENV_BIN="$ROOT_DIR/.venv/bin"
elif [ -d "$ROOT_DIR/backend/.venv" ]; then
    VENV_BIN="$ROOT_DIR/backend/.venv/bin"
else
    echo "Error: Virtual environment not found."
    echo "Please initialize the environment:"
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/pip install -r backend/requirements.txt"
    exit 1
fi

# Ensure local .env exists
if [ ! -f "$ROOT_DIR/.env" ] && [ -f "$ROOT_DIR/.env.example" ]; then
    echo "Initializing .env from .env.example..."
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

export PYTHONPATH="$ROOT_DIR/backend"
cd "$ROOT_DIR/backend"

echo "Launching FastAPI server on http://0.0.0.0:8000 (Docs at http://localhost:8000/docs)..."
exec "$VENV_BIN/uvicorn" app.main:app --host 0.0.0.0 --port 8000
