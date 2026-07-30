import streamlit as st
from groq import Groq
import tempfile, os
from datetime import datetime

st.set_page_config(page_title="DoneForYou", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    /* FORCE LIGHT THEME */
    .stApp { background-color: #fdfcfb !important; }
    [data-testid="stSidebar"] { background-color: #f8f7f5 !important; border-right: 1px solid #e5e7eb; }
    
    /* FORCE DARK TEXT EVERYWHERE */
    h1, h2, h3, h4, p, span, div, label {
        color: #111827 !important;
    }
    [data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
    }
    
    /* Fix uploader */
    [data-testid="stFileUploader"] {
        background: white !important;
        border: 2px dashed #d1d5db !important;
        border-radius: 16px !important;
        padding: 40px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #111827 !important;
    }
    /* Hide ugly drag text */
    [data-testid="stFileUploader"] small {
        color: #6b7280 !important;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }
    
    /* Button */
    button[kind="primary"] {
        background-color: #1e293b !important;
        color: white !important;
        border-radius: 10px !important;
    }
    button[kind="primary"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

if "notes" not in st.session_state:
    st.session_state.notes = []
if "current_note" not in st.session_state:
    st.session_state.current_note = None

groq_key = st.secrets.get("GROQ_API_KEY")
if not groq_key:
    st.stop()
client = Groq(api_key=groq_key)

# SIDEBAR
with st.sidebar:
    st.markdown("## 🎙️ DoneForYou")
    if st.button("＋ New Meeting Note", use_container_width=True, type="primary"):
        st.session_state.current_note = None
        st.rerun()
    st.markdown("---")
    st.caption("PAST MEETINGS")
    if not st.session_state.notes:
        st.markdown("<div style='text-align:center; margin-top:40px;'><div style='font-size:24px;'>🗃️</div><div style='color:#6b7280; margin-top:8px;'>No notes yet</div></div>", unsafe_allow_html=True)
    else:
        for note in reversed(st.session_state.notes):
            if st.button(note['title'], key=note['title']+note['date'], use_container_width=True):
                st.session_state.current_note = note
                st.rerun()

# MAIN VIEW - past
