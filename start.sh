#!/bin/bash

# Start FastAPI backend in the background
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &

# Capture the PID of the background process
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 3

# Start Streamlit frontend in the foreground
streamlit run app.py --server.port 5000

# If Streamlit is terminated, kill the backend process
kill $BACKEND_PID