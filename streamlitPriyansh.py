# Example Streamlit frontend integration
import streamlit as st
import requests

BACKEND_URL = "https://auto-resume-portfolio.onrender.com"

if st.button("Check Backend Status"):
    response = requests.get(f"{BACKEND_URL}/health")
    if response.ok:
        st.success("Backend is healthy!")
    else:
        st.error("Backend issue detected!")
