#!/bin/bash

# Setup script for Agentic Commerce AI Chatbot

echo "🚀 Setting up Agentic Commerce AI Chatbot..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p agent_memory/{procedural,episodic,semantic,patterns,cache,checkpoints}

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
    else
        echo "⚠️  Ollama is not running. Starting Ollama..."
        ollama serve &
        sleep 5
    fi
    
    # Pull required models
    echo "🤖 Pulling required models..."
    ollama pull llama3.1:8b
    ollama pull nomic-embed-text
    
    echo "💡 For better performance, consider pulling larger models:"
    echo "   ollama pull llama3.1:70b"
    echo "   ollama pull mixtral:8x7b"
else
    echo "❌ Ollama is not installed!"
    echo "Please install Ollama from: https://ollama.com/download"
    echo "After installation, run:"
    echo "   ollama pull llama3.1:8b"
    echo "   ollama pull nomic-embed-text"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Agentic Commerce AI Chatbot Configuration

# Backend settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Memory settings
MEMORY_PATH=./agent_memory

# Dashboard settings
DASHBOARD_URL=http://localhost:8050
EOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Start the backend: python backend/main.py"
echo "3. Integrate with your dashboard (see README.md)"
echo ""
echo "🔧 Configuration:"
echo "- Edit .env for custom settings"
echo "- Larger models provide better quality (but need more RAM)"
echo "- Check agent_memory/ for persistent storage"