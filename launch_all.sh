#!/bin/bash

echo "🚀 Launching Agentic Commerce Dashboard with AI Assistant"
echo "========================================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama is not running. Please start Ollama first."
    echo "   On macOS: Open the Ollama app"
    exit 1
fi

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8050 | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend
echo "✅ Starting AI backend..."
cd "$SCRIPT_DIR/agentic-commerce-chatbot"
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found in agentic-commerce-chatbot/venv"
    echo "   Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements_simple.txt
fi
python backend/main_simple.py &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start dashboard
echo "✅ Starting dashboard..."
# Check if we have a parent venv
if [ -d "$SCRIPT_DIR/../.venv" ]; then
    echo "   Using parent virtual environment..."
    source "$SCRIPT_DIR/../.venv/bin/activate"
fi
python dashboard_enhanced.py &
DASHBOARD_PID=$!

# Wait a moment
sleep 2

echo ""
echo "========================================================"
echo "✅ All systems running!"
echo ""
echo "📊 Dashboard: http://127.0.0.1:8050/"
echo "🤖 AI Backend: http://localhost:8000/"
echo ""
echo "💬 To use AI Assistant:"
echo "   1. Open http://127.0.0.1:8050/ in your browser"
echo "   2. Click '💬 AI Assistant' button in bottom-right"
echo "   3. Chat with the AI to modify dashboard variables!"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo "========================================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8050 | xargs kill -9 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Keep script running
wait