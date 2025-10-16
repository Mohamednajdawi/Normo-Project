#!/bin/bash

# Normo Legal Assistant - Startup Script
# This script starts both the backend and frontend servers

echo "🏗️  Starting Normo Legal Assistant..."
echo "================================================"

# Check if required directories exist
if [ ! -d "normo_backend" ]; then
    echo "❌ Backend directory not found!"
    exit 1
fi

if [ ! -d "normo_frontend" ]; then
    echo "❌ Frontend directory not found!"
    exit 1
fi

# Function to kill background processes on exit
cleanup() {
    echo
    echo "🛑 Shutting down Normo Legal Assistant..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait
    echo "✅ Shutdown complete!"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
cd normo_backend
source .env 2>/dev/null || true
PYTHONPATH=$(pwd)/src uv run python -m normo_backend.main &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 5

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
else
    echo "❌ Failed to start backend!"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd normo_frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend is running
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
else
    echo "❌ Failed to start frontend!"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo
echo "🚀 Normo Legal Assistant is now running!"
echo "================================================"
echo "📚 Backend API: http://localhost:8000"
echo "🎨 Frontend UI:  http://localhost:3000"
echo "📖 API Docs:    http://localhost:8000/docs"
echo "================================================"
echo "Press Ctrl+C to stop all services"
echo

# Wait for user interrupt
wait
