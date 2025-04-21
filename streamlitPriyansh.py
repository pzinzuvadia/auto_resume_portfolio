"""
Streamlit deployment file for AI Portfolio Generator
This file starts both the FastAPI backend and Streamlit frontend
"""
import subprocess
import threading
import time
import streamlit as st
import sys
import os
import requests

# Set page configuration
st.set_page_config(
    page_title="AI Portfolio Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state properly
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

# Check for required environment variables
required_vars = ["ANTHROPIC_API_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.info("Please set these variables in your Streamlit Cloud secrets.")
    st.stop()

# Function to start the backend
def start_backend():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

# Check if backend is already running
def is_backend_running():
    try:
        response = requests.get("http://127.0.0.1:8000/docs")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

# Start backend if not running
if not is_backend_running():
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    time.sleep(5)  # Give backend some time to start

# Import and run the main Streamlit app
import app
app.main()
