#!/bin/bash

echo "🚀 Starting Smart Forest Fire Prevention System..."
echo ""

# Start backend in background
echo "Starting FastAPI backend..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

sleep 3

# Start sensor ingestion in background
echo "Starting sensor ingestion service..."
cd backend
python sensor_ingestion.py &
SENSOR_PID=$!
cd ..

sleep 2

# Start frontend
echo "Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Sensor PID: $SENSOR_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "🌐 Access the dashboard at: http://localhost:3000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait and cleanup on exit
trap "kill $BACKEND_PID $SENSOR_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
