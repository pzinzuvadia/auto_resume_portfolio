#!/bin/bash

# Ensure clean exit behavior
cleanup() {
    echo "Shutting down services..."
    
    # Kill FastAPI backend if running
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend server (PID: $BACKEND_PID)"
        kill -TERM $BACKEND_PID 2>/dev/null || true
    fi
    
    exit 0
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM EXIT

# Start FastAPI backend in the background
echo "Starting FastAPI backend..."
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &

# Capture the PID of the background process
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait a moment for the backend to start
echo "Waiting for backend to start..."
sleep 3

# Start Streamlit frontend in the foreground
echo "Starting Streamlit frontend..."
streamlit run app.py --server.port 5000