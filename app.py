import streamlit as st
from groq import Groq
import tempfile, os
from datetime import datetime

st.set_page_config(page_title="DoneForYou", page_icon="🎙️", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# THEME COLORS
if st.session_state.dark_mode:
    bg, card_bg, text, subtext, border, btn_bg, btn_text = "#0e1117", "#1e222b", "#ffffff", "#9ca3af", "#2a2e39", "#262b36", "#ffffff"
else:
    bg, card_bg, text, subtext, border, btn_bg, btn_text = "#fdfcfb", "#ffffff", "#111827", "#6b7280", "#e5e7eb", "#111827", "#ffffff"

st.markdown(f"""
<style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    [data-testid="stToolbar"] {{visibility: hidden!important;}}.stDeployButton {{display: none!important;}}

  .stApp {{ background-color: {bg}!important; }}
    [data-testid="stSidebar"] {{ background-color: {card_bg}!important; border-right: 1px solid {border}; }}

    h1, h2, h3, p, div, span, label {{ color: {text}!important; }}

    /* --- FIX FOR UPLOADER --- */
    [data-testid="stFileUploader"] {{
        background: {card_bg}!important;
        border: 2px dashed {border}!important;
        border-radius: 16px!important;
    }}
    /* The small dark upload button inside */
    [data-testid="stFileUploader"] button {{
        background-color: {btn_bg}!important;
        color: {btn_text}!important;
        border: 1px solid {border}!important;
    }}
    [data-testid="stFileUploader"] button * {{
        color: {btn_text}!important;
    }}
    /* The "200MB per file" text */
    [data-testid="stFileUploader"] small {{
        color: {subtext}!important;
    }}
</style>
""", unsafe_allow_html=True)

if "notes" not in st.session_state:
    st.session_state.notes = []
if "current_note" not in st.session_state:
    st.session_state.current_note = None

groq_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=groq_key) if groq_key else None

with st.sidebar:
    st.markdown(f"## 🎙️ DoneForYou")
    if st.button("＋ New Meeting Note", use_container_width=True, type="primary"):
        st.session_state.current_note = None
        st.rerun()
    st.markdown("---")
    st.toggle("🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode", value=st.session_state.dark_mode, on_change=toggle_theme)
    st.markdown("---")
    st.caption("PAST MEETINGS")
    if not st.session_state.notes:
        st.caption("No notes yet")
    else:
        for n in reversed(st.session_state.notes):
            if st.button(n['title'], key=n['date'], use_container_width=True):
                st.session_state.current_note = n
                st.rerun()

if st.session_state.current_note:
    st.title(st.session_state.current_note['title'])
    st.caption(st.session_state.current_note['date'])
    st.divider()
    st.markdown(st.session_state.current_note['content'])
    if st.button("← Back"):
        st.session_state.current_note = None
        st.rerun()
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)
st.title("Your meetings, summarized.")
st.write("Upload your audio. We'll transcribe the conversation, extract action items, and draft a follow-up email instantly.")
st.markdown("<br>", unsafe_allow_html=True)

uploaded = st.file_uploader("Drop your audio file here", type=["mp3","m4a","wav","mp4"])
st.caption("Click to upload or drag and drop • Supports MP3, WAV, M4A • 200MB max")

if uploaded and client:
    with st.spinner("✨ Working magic..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(file=(tmp_path, f.read()), model="whisper-large-v3", response_format="text")
        os.unlink(tmp_path)
        text = transcription if isinstance(transcription, str) else str(transcription)
        chat = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content": f"Format as ## Summary, ## Action Items, ## Follow-up Email:\n{text[:12000]}"}])
        result = chat.choices[0].message.content
    st.divider()
    st.markdown(result)
    title = f"Meeting {datetime.now().strftime('%b %d %I:%M %p')}"
    st.session_state.notes.append({"title": title, "date": datetime.now().strftime('%Y-%m-%d %H:%M'), "content": result})
    st.download_button("Download Notes", result, file_name="notes.txt")
