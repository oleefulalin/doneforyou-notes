import streamlit as st
from groq import Groq
import tempfile, os
from datetime import datetime

st.set_page_config(page_title="DoneForYou", page_icon="🎙️", layout="wide")

# --- CSS TO MATCH YOUR SCREENSHOT ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #f8f7f5; border-right: 1px solid #eee; }
    .stApp { background-color: #fdfcfb; }
    h1 { font-family: 'Georgia', serif; font-weight: 800!important; color: #111827!important; }
    .upload-card {
        border: 2px dashed #e5e7eb; background: white;
        border-radius: 16px; padding: 80px 20px; text-align: center;
    }
    .past-item {
        background: white; border: 1px solid #eee; padding: 12px;
        border-radius: 10px; margin-bottom: 8px; font-size: 14px;
    }
    div[data-testid="stFileUploader"] { 
        border: 2px dashed #e5e7eb!important; border-radius: 16px!important;
        background: white!important; padding: 60px 20px!important;
    }
</style>
""", unsafe_allow_html=True)

if "notes" not in st.session_state:
    st.session_state.notes = []

groq_key = st.secrets.get("GROQ_API_KEY")
if not groq_key:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()
client = Groq(api_key=groq_key)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("
