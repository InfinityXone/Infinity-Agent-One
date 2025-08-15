#!/bin/bash
BASE_DIR=~/Downloads/agent_one
VENV_DIR="$BASE_DIR/venv"
LOG_DIR="$BASE_DIR/logs"
API_MODULE="api:app"
PORT=8001

mkdir -p "$LOG_DIR"

echo "===== 🚀 Launching Agent One API (Port $PORT) ====="

# Kill any process using this port
if lsof -i:$PORT -t >/dev/null; then
    echo "⚠️  Port $PORT in use, killing process..."
    lsof -i:$PORT -t | xargs kill -9
fi

# Activate venv
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Virtual environment not found. Run: cd $BASE_DIR && python3 -m venv venv && source venv/bin/activate && pip install fastapi uvicorn supabase"
    exit 1
fi

# Check that API module exists
if ! python -c "import importlib; importlib.import_module('api')"; then
    echo "❌ API module 'api' not found in $BASE_DIR"
    exit 1
fi

# Launch API with auto-reload and logging
nohup uvicorn "$API_MODULE" --host 0.0.0.0 --port $PORT --reload > "$LOG_DIR/api.log" 2>&1 &

# Wait briefly and check if running
sleep 3
if lsof -i:$PORT -t >/dev/null; then
    echo "✅ Agent One API running at http://0.0.0.0:$PORT"
else
    echo "❌ Failed to start Agent One API. Check $LOG_DIR/api.log"
fi
