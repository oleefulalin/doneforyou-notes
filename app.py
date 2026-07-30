import streamlit as st
from groq import Groq
import tempfile
import os

st.set_page_config(page_title="DoneForYou Notes", page_icon="✨", layout="wide")

# BEAUTIFUL CSS
st.markdown("""
<style>
   .stApp { background-color: #0a0a0a; }
   .main-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #252525 100%);
        padding: 30px; border-radius: 20px; border: 1px solid #333;
    }
   .feature-box {
        background: #1e1e1e; padding: 20px; border-radius: 15px;
        border: 1px solid #2a2a2a; text-align: center;
    }
    h1 { font-size: 3rem!important; font-weight: 800!important; }
   .upload-box { border: 2px dashed #555!important; border-radius: 20px!important; }
</style>
""", unsafe_allow_html=True)

# HEADER
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("# ✨ DoneForYou Notes")
    st.markdown("### Turn any meeting into action items in 30 seconds. No more note-taking.")
    st.markdown("Built for realtors, recruiters, founders, and anyone who hates typing notes.")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="feature-box">⚡️ <b>30 sec</b><br>Average time</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# FEATURES
c1, c2, c3 = st.columns(3)
with c1: st.markdown('<div class="feature-box">📝 <b>Smart Summary</b><br>3 bullets, no fluff</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="feature-box">✅ <b>Action Items</b><br>Who does what by when</div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="feature-box">📧 <b>Follow-up Email</b><br>Ready to copy-paste</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# APP LOGIC
groq_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else None
if not groq_key:
    groq_key = st.text_input("Paste Groq key", type="password")
    if not groq_key: st.stop()

client = Groq(api_key=groq_key)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("#### 🎙️ Drop your meeting audio here")
uploaded = st.file_uploader("", type=["mp3","m4a","wav","mp4"], label_visibility="collapsed")
st.caption("Works with Zoom, Google Meet, iPhone voice memos, WhatsApp audio • Max 200MB")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded:
    with st.status("✨ Working my magic...", expanded=True) as status:
        st.write("🎧 Transcribing audio...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, f.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        os.unlink(tmp_path)
        st.write("🧠 Writing summary + action items...")
        transcript_text = transcription if isinstance(transcription, str) else str(transcription)
        summary = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content": f"You are a world-class executive assistant. Format with emojis and clean sections:\n\n## 📌 Summary (3 bullets)\n## ✅ Action Items (format: Person: Task - Deadline)\n## 📧 Follow-up Email (professional, ready to send)\n\nTranscript:\n{transcript_text[:12000]}"}]
        )
        status.update(label="✅ Done!", state="complete", expanded=False)

    result = summary.choices[0].message.content

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(result)

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button("📥 Download Notes", result, file_name="meeting_notes.txt", use_container_width=True)
    with col_b:
        if st.button("🔄 Process another meeting", use_container_width=True):
            st.rerun()
