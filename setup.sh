#!/bin/bash

echo "🔥 Smart Forest Fire Prevention System - Quick Start"
echo "=================================================="
echo ""

# Check if MongoDB is running
echo "📦 Checking MongoDB..."
if ! mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "⚠️  MongoDB is not running. Starting with Docker..."
    docker run -d -p 27017:27017 --name mongodb mongo:latest
    sleep 3
fi
echo "✅ MongoDB is running"
echo ""

# Setup Backend
echo "🔧 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

echo "✅ Backend setup complete"
echo ""

# Setup Frontend
echo "🎨 Setting up Frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install --silent
fi

echo "✅ Frontend setup complete"
echo ""

# Instructions
echo "🚀 Ready to start!"
echo "=================================================="
echo ""
echo "To run the system, open 3 terminals:"
echo ""
echo "Terminal 1 - FastAPI Backend:"
echo "  cd backend && source venv/bin/activate && python main.py"
echo ""
echo "Terminal 2 - Sensor Ingestion:"
echo "  cd backend && source venv/bin/activate && python sensor_ingestion.py"
echo ""
echo "Terminal 3 - Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "📚 See README.md for detailed documentation"
