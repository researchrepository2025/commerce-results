#!/bin/bash

echo "🚀 Launching Agentic Commerce AI Chatbot"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama is not running. Please start Ollama first."
    echo "   On macOS: Open the Ollama app"
    echo "   On Linux: Run 'ollama serve' in another terminal"
    exit 1
fi

# Kill any existing process on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "🔄 Stopping existing server on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "✅ Starting backend server..."
echo ""
echo "📋 Usage Instructions:"
echo "   1. Run the dashboard: python ../dashboard_enhanced.py"
echo "   2. Open http://127.0.0.1:8050/ in your browser"
echo "   3. Click the '💬 AI Assistant' button in bottom-right corner"
echo ""
echo "🌐 API Endpoints:"
echo "   - Health Check: http://localhost:8000/api/health"
echo "   - WebSocket: ws://localhost:8000/ws/agent"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run the server
python backend/main_simple.py