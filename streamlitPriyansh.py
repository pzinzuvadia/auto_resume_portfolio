import streamlit as st
import requests

st.set_page_config(page_title="AI Portfolio Generator", page_icon="🚀", layout="wide")

st.title("🚀 AI Portfolio Generator")

BACKEND_URL = "https://auto-resume-portfolio.onrender.com"

st.write("Click the button below to check if the backend is live:")

if st.button("Check Backend Status"):
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.ok:
            st.success("✅ Backend is healthy!")
        else:
            st.error("❌ Backend issue detected.")
    except Exception as e:
        st.error(f"⚠️ Could not reach backend: {e}")
