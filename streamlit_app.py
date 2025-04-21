import streamlit as st
import requests

st.set_page_config(page_title="AI Portfolio Generator", page_icon="🚀", layout="wide")
st.title("🚀 AI Portfolio Generator")

BACKEND_URL = "https://auto-resume-portfolio.onrender.com"

st.write("Click the button below to check if the backend is live:")

try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=3)
    if response.ok:
        st.success("Backend is connected ✅")
    else:
        st.warning("Backend responded, but not OK ❗️")
except Exception as e:
    st.warning(f"Could not connect to backend: {e}")

if st.button("Check Backend Again"):
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if response.ok:
            st.success("Backend is healthy!")
        else:
            st.error("Backend returned an error.")
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
