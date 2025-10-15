#!/bin/bash

echo "🚀 Starting Week 7 Automation Bias Analysis"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install flask-cors if not already installed
echo "🔧 Installing dependencies..."
pip install flask-cors

# Kill any existing API server
echo "🔄 Stopping any existing API servers..."
pkill -f week7_api.py 2>/dev/null || true

# Start the API server
echo "🌐 Starting API server on port 5002..."
python week7_api.py &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to start..."
sleep 3

# Test the API
echo "🧪 Testing API connection..."
if curl -s http://localhost:5002/api/analyze?topic=test > /dev/null; then
    echo "✅ API server is running successfully!"
    echo "🌐 Open week7.html in your browser to use the interface"
    echo "📊 Or run: python week7.py for command line analysis"
    echo ""
    echo "🔗 API available at: http://localhost:5002"
    echo "📄 HTML interface: week7.html"
    echo "🐍 Command line: python week7.py"
    echo ""
    echo "Press Ctrl+C to stop the API server"
    
    # Keep the script running
    wait $API_PID
else
    echo "❌ API server failed to start"
    echo "🔍 Check the error messages above"
    exit 1
fi
