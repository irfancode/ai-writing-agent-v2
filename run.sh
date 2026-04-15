#!/bin/bash
# AI Writing Agent - Universal Launcher

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ "$1" = "setup" ]; then
    bash setup.sh
    exit $?
fi

# Check if .venv exists
if [ -d ".venv" ]; then
    PYTHON=".venv/bin/python"
elif [ -d "venv" ]; then
    PYTHON="venv/bin/python"
else
    echo "Error: Virtual environment not found."
    echo "Run: ./run.sh setup"
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
elif [ "$1" = "init" ]; then
    echo "Initializing AI Writing Agent..."
    "$PYTHON" -m src.cli.main onboard
elif [ "$1" = "test" ]; then
    echo "Running tests..."
    "$PYTHON" -m pytest tests/ -v
else
    "$PYTHON" -m src.cli.main "$@"
fi
