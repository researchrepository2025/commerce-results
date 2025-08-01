#!/bin/bash

echo "🚀 Launching Standalone Agentic Commerce Dashboard"
echo "================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import dash" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "✅ Starting dashboard server..."
echo ""
echo "📊 Dashboard Features:"
echo "   - Consumer market analysis by generation"
echo "   - Business spending by industry"
echo "   - Government spending projections"
echo "   - Revenue distribution modeling"
echo "   - 30+ interactive visualizations"
echo ""
echo "🌐 Opening browser at: http://127.0.0.1:8050/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================="
echo ""

# Run the dashboard
python dashboard_no_ai.py