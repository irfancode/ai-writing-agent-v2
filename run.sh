#!/bin/bash
# AI Writing Agent - Universal Launcher
# Usage: ./run.sh [command]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .venv exists
if [ -d ".venv" ]; then
    PYTHON=".venv/bin/python"
elif [ -d "venv" ]; then
    PYTHON="venv/bin/python"
else
    echo "Error: No virtual environment found. Run: python3 -m venv .venv && .venv/bin/pip install -e ."
    exit 1
fi

# Run the command
if [ "$1" = "gui" ]; then
    "$PYTHON" -m src.cli.main gui
elif [ "$1" = "tui" ]; then
    "$PYTHON" -m src.cli.main tui
elif [ "$1" = "server" ]; then
    "$PYTHON" -m src.api.server
elif [ "$1" = "web" ]; then
    echo "Starting API server..."
    "$PYTHON" -m src.api.server &
    SERVER_PID=$!
    sleep 2
    echo "Starting frontend..."
    cd frontend && npm run dev &
    echo "WebGUI running at http://localhost:5173"
    echo "Press Ctrl+C to stop both servers"
    trap "kill $SERVER_PID 2>/dev/null" EXIT
    wait
else
    "$PYTHON" -m src.cli.main "$@"
fi
