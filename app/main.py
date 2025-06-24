# ==========================================
# ULTRA MINIMAL MAIN.PY - EMERGENCY FIX
# Untuk mengatasi Streamlit Cloud connection refused
# ==========================================

import streamlit as st

# Basic page config - MINIMAL
st.set_page_config(
    page_title="ASTHA Test",
    page_icon="🕌"
)

# Ultra simple content
st.title("🕌 ASTHA HAJJ ANALYTICS")
st.write("✅ Aplikasi berhasil deploy!")

# Simple metric
st.metric("Status Deployment", "Success", "✅")

# Success message
st.success("🎉 Streamlit Cloud deployment berhasil!")

st.write("Dashboard lengkap akan segera tersedia.")
