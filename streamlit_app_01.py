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

# Set page configuration
st.set_page_config(
    page_title="AI Portfolio Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for required environment variables
required_vars = ["ANTHROPIC_API_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.info("Please set these variables in your Streamlit Cloud secrets.")
    st.stop()

# Start FastAPI backend in a separate thread
# def start_backend():
#     try:
#         process = subprocess.Popen(
#             [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         # Wait for the backend to start
#         time.sleep(5)
#         return process
#     except Exception as e:
#         st.error(f"Error starting backend: {str(e)}")
#         return None

# # Start backend in a thread
# backend_thread = threading.Thread(target=start_backend)
# backend_thread.daemon = True
# backend_thread.start()

# The backend URL on Render
BACKEND_URL = "https://auto-resume-portfolio.onrender.com"

st.write("Click the button below to check the backend status:")

# Check on load (root path)
try:
    res = requests.get(f"{BACKEND_URL}/", timeout=3)
    if res.ok:
        st.success("✅ Backend is live and responding.")
    else:
        st.warning("⚠️ Backend responded with a non-200 status.")
except Exception as e:
    st.warning(f"⚠️ Could not reach backend: {e}")


# Wait for backend to start
time.sleep(5)

# Import and run the main Streamlit app
import app
app.main()
