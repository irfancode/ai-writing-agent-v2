#!/bin/bash

set -e

echo "🚀 AI Writing Agent - Quick Setup"
echo "=================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "Step 1: Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

echo ""
echo "Step 2: Activating environment..."
source .venv/bin/activate

echo ""
echo "Step 3: Installing dependencies..."
pip install -e . -q

echo ""
echo "Step 4: Checking available AI providers..."

check_ollama() {
    if command -v ollama &> /dev/null; then
        if curl -s http://localhost:11434/ > /dev/null 2>&1; then
            echo "  ✓ Ollama is running"
            OLLAMA_AVAILABLE=true
        else
            echo "  ○ Ollama installed but not running (optional)"
            OLLAMA_AVAILABLE=false
        fi
    else
        echo "  ○ Ollama not installed (optional - for local AI)"
        OLLAMA_AVAILABLE=false
    fi
}

check_groq() {
    if [ -n "$GROQ_API_KEY" ]; then
        echo "  ✓ GROQ_API_KEY detected"
        GROQ_AVAILABLE=true
    else
        echo "  ○ GROQ_API_KEY not set (optional)"
        GROQ_AVAILABLE=false
    fi
}

check_together() {
    if [ -n "$TOGETHER_API_KEY" ]; then
        echo "  ✓ TOGETHER_API_KEY detected"
        TOGETHER_AVAILABLE=true
    else
        echo "  ○ TOGETHER_API_KEY not set (optional)"
        TOGETHER_AVAILABLE=false
    fi
}

check_ollama
check_groq
check_together

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Quick Start Commands:"
echo "  ./run.sh write 'Write a haiku about AI'"
echo "  ./run.sh think 'Plan a blog post'"
echo "  ./run.sh interactive"
echo "  ./run.sh gui        # Desktop app"
echo "  ./run.sh web       # Web interface"
echo "  ./run.sh server    # API server"
echo ""

if [ "$OLLAMA_AVAILABLE" = false ] && [ "$GROQ_AVAILABLE" = false ] && [ "$TOGETHER_AVAILABLE" = false ]; then
    echo "⚠️  No AI provider detected. For real AI, choose one:"
    echo ""
    echo "  Option 1: Ollama (local, private)"
    echo "    brew install ollama"
    echo "    ollama pull llama3.2"
    echo ""
    echo "  Option 2: Groq (fast, free tier)"
    echo "    Get free key: https://console.groq.com/keys"
    echo "    export GROQ_API_KEY=your_key_here"
    echo ""
    echo "  Option 3: Together AI (reasoning models)"
    echo "    Get free key: https://api.together.xyz/settings/api-keys"
    echo "    export TOGETHER_API_KEY=your_key_here"
fi

echo ""
echo "Ready to write! ✍️"
