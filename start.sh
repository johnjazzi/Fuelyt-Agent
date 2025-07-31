#!/bin/bash

# Fuelyt AI Agent - Local Development Startup Script

echo "🏃‍♂️ Starting Fuelyt AI Agent Development Environment"
echo "======================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the Fuelyt project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.8+ is required. Current version: $(python3 --version)"
    exit 1
fi

echo "✅ Python version check passed: $(python3 --version)"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set"
    echo "   Set it with: export OPENAI_API_KEY='your-api-key-here'"
    echo "   The application may not function properly without it."
    echo ""
fi

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Function to start backend
start_backend() {
    echo "🚀 Starting backend server on port 8000..."
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting frontend server on port 3000..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   Frontend server stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🚀 Starting services..."
echo ""

# Start backend
start_backend
sleep 3

# Start frontend
start_frontend
sleep 3

echo ""
echo "✅ Fuelyt AI Agent is now running!"
echo ""
echo "🌐 Frontend:  http://localhost:3000"
echo "📡 Backend:   http://localhost:8000"
echo "📖 API Docs:  http://localhost:8000/docs"
echo ""
echo "💡 Try these test commands:"
echo "   • python local_test.py      # Test the serverless handler"
echo "   • python example_usage.py   # Test the API endpoints"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait