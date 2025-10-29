#!/bin/bash
# HireSight Backend Startup Script

echo "=========================================="
echo "🚀 HireSight Backend Setup & Launch"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip found: $(pip3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create uploads directory
mkdir -p uploads
echo "✅ Upload directory ready"

# Set environment variables (optional)
export DEBUG=True
export PORT=5000

echo ""
echo "=========================================="
echo "🎯 Starting HireSight API Server"
echo "=========================================="
echo "📍 Server will run at: http://localhost:5000"
echo "📖 API Documentation: See README.md"
echo "⏹️  Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start the server
python api.py
